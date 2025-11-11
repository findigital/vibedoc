"""
Authentication and session management for VibeDoc SaaS
Handles user login, signup, session management, and authorization
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from functools import wraps
import jwt
from models import User, Subscription, SubscriptionTier, SubscriptionStatus

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

class AuthError(Exception):
    """Authentication error"""
    pass

class AuthService:
    """Authentication service"""

    def __init__(self, db_session):
        self.db = db_session

    def register_user(self, email: str, username: str, password: str, full_name: str = "") -> Tuple[bool, str, Optional[User]]:
        """
        Register a new user

        Returns:
            Tuple[bool, str, Optional[User]]: (success, message, user)
        """
        # Validate input
        if not email or not username or not password:
            return False, "Email, username, and password are required", None

        if len(password) < 8:
            return False, "Password must be at least 8 characters", None

        # Check if user already exists
        existing_user = self.db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()

        if existing_user:
            if existing_user.email == email:
                return False, "Email already registered", None
            else:
                return False, "Username already taken", None

        # Create new user
        try:
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                email_verified=False  # Require email verification in production
            )
            user.set_password(password)
            user.generate_api_key()
            user.generate_verification_token()

            self.db.add(user)
            self.db.flush()  # Get user.id

            # Create free subscription
            subscription = Subscription(
                user_id=user.id,
                tier=SubscriptionTier.FREE,
                status=SubscriptionStatus.ACTIVE,
                plan_generation_limit=5,
                project_limit=3,
                export_limit=10,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30)
            )

            self.db.add(subscription)
            self.db.commit()

            return True, "User registered successfully", user

        except Exception as e:
            self.db.rollback()
            return False, f"Registration failed: {str(e)}", None

    def authenticate_user(self, email_or_username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        Authenticate user with email/username and password

        Returns:
            Tuple[bool, str, Optional[User]]: (success, message, user)
        """
        if not email_or_username or not password:
            return False, "Email/username and password are required", None

        # Find user by email or username
        user = self.db.query(User).filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()

        if not user:
            return False, "Invalid credentials", None

        if not user.is_active:
            return False, "Account is disabled", None

        if not user.check_password(password):
            return False, "Invalid credentials", None

        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()

        return True, "Login successful", user

    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate using API key"""
        if not api_key or not api_key.startswith("vbd_"):
            return None

        user = self.db.query(User).filter(User.api_key == api_key).first()

        if user and user.is_active:
            return user

        return None

    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "is_admin": user.is_admin,
            "exp": expire,
            "iat": datetime.utcnow()
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        payload = {
            "sub": str(user.id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None

    def get_user_by_token(self, token: str) -> Optional[User]:
        """Get user from JWT token"""
        payload = self.verify_token(token)
        if not payload:
            return None

        user_id = int(payload.get("sub"))
        return self.db.query(User).filter(User.id == user_id).first()

    def change_password(self, user: User, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        if not user.check_password(old_password):
            return False, "Current password is incorrect"

        if len(new_password) < 8:
            return False, "New password must be at least 8 characters"

        user.set_password(new_password)
        self.db.commit()

        return True, "Password changed successfully"

    def request_password_reset(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """Request password reset token"""
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            # Don't reveal if email exists
            return True, "If the email exists, a reset link has been sent", None

        reset_token = user.generate_reset_token()
        self.db.commit()

        return True, "Reset token generated", reset_token

    def reset_password(self, reset_token: str, new_password: str) -> Tuple[bool, str]:
        """Reset password using token"""
        user = self.db.query(User).filter(User.reset_token == reset_token).first()

        if not user:
            return False, "Invalid reset token"

        if user.reset_token_expires < datetime.utcnow():
            return False, "Reset token has expired"

        if len(new_password) < 8:
            return False, "Password must be at least 8 characters"

        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        self.db.commit()

        return True, "Password reset successfully"

    def verify_email(self, verification_token: str) -> Tuple[bool, str]:
        """Verify user email"""
        user = self.db.query(User).filter(User.verification_token == verification_token).first()

        if not user:
            return False, "Invalid verification token"

        user.email_verified = True
        user.verification_token = None
        self.db.commit()

        return True, "Email verified successfully"

    def regenerate_api_key(self, user: User) -> str:
        """Regenerate user's API key"""
        new_key = user.generate_api_key()
        self.db.commit()
        return new_key

class SessionManager:
    """Gradio session manager for storing user state"""

    def __init__(self):
        self.sessions = {}

    def create_session(self, session_id: str, user: User, access_token: str):
        """Create user session"""
        self.sessions[session_id] = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'access_token': access_token,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow()
        }

    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        session = self.sessions.get(session_id)
        if session:
            session['last_activity'] = datetime.utcnow()
        return session

    def delete_session(self, session_id: str):
        """Delete session (logout)"""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def is_authenticated(self, session_id: str) -> bool:
        """Check if session is authenticated"""
        return session_id in self.sessions

    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """Remove expired sessions"""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        expired = [
            sid for sid, session in self.sessions.items()
            if session['last_activity'] < cutoff
        ]
        for sid in expired:
            del self.sessions[sid]

# Global session manager
session_manager = SessionManager()

def require_auth(f):
    """Decorator to require authentication for Gradio functions"""
    @wraps(f)
    def wrapper(session_id, *args, **kwargs):
        if not session_manager.is_authenticated(session_id):
            raise AuthError("Authentication required")
        return f(session_id, *args, **kwargs)
    return wrapper

def require_admin(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def wrapper(session_id, *args, **kwargs):
        session = session_manager.get_session(session_id)
        if not session or not session.get('is_admin'):
            raise AuthError("Admin privileges required")
        return f(session_id, *args, **kwargs)
    return wrapper
