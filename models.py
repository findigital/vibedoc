"""
Database models for VibeDoc SaaS application
Supports user management, subscriptions, projects, and usage tracking
"""

from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum
import bcrypt
import secrets

Base = declarative_base()

class SubscriptionTier(enum.Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"

class User(Base):
    """User model"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))

    # Authentication
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String(100))
    reset_token = Column(String(100))
    reset_token_expires = Column(DateTime)

    # API access
    api_key = Column(String(100), unique=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def generate_api_key(self) -> str:
        """Generate new API key"""
        self.api_key = f"vbd_{secrets.token_urlsafe(32)}"
        return self.api_key

    def generate_verification_token(self) -> str:
        """Generate email verification token"""
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token

    def generate_reset_token(self, expires_hours: int = 24) -> str:
        """Generate password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=expires_hours)
        return self.reset_token

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Subscription(Base):
    """Subscription model"""
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)

    # Subscription details
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)

    # Usage limits (per month)
    plan_generation_limit = Column(Integer, default=5)  # Free: 5, Pro: 50, Enterprise: unlimited (-1)
    project_limit = Column(Integer, default=3)  # Free: 3, Pro: 20, Enterprise: unlimited (-1)
    export_limit = Column(Integer, default=10)  # Free: 10, Pro: 200, Enterprise: unlimited (-1)

    # Usage tracking (current month)
    plans_generated = Column(Integer, default=0)
    projects_created = Column(Integer, default=0)
    exports_made = Column(Integer, default=0)

    # Billing
    stripe_customer_id = Column(String(100), unique=True)
    stripe_subscription_id = Column(String(100), unique=True)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")

    def reset_monthly_usage(self):
        """Reset monthly usage counters"""
        self.plans_generated = 0
        self.projects_created = 0
        self.exports_made = 0

    def can_generate_plan(self) -> bool:
        """Check if user can generate another plan"""
        if self.plan_generation_limit == -1:  # Unlimited
            return True
        return self.plans_generated < self.plan_generation_limit

    def can_create_project(self) -> bool:
        """Check if user can create another project"""
        if self.project_limit == -1:  # Unlimited
            return True
        return self.projects_created < self.project_limit

    def can_export(self) -> bool:
        """Check if user can make another export"""
        if self.export_limit == -1:  # Unlimited
            return True
        return self.exports_made < self.export_limit

    def upgrade_to_pro(self):
        """Upgrade subscription to Pro tier"""
        self.tier = SubscriptionTier.PRO
        self.plan_generation_limit = 50
        self.project_limit = 20
        self.export_limit = 200

    def upgrade_to_enterprise(self):
        """Upgrade subscription to Enterprise tier"""
        self.tier = SubscriptionTier.ENTERPRISE
        self.plan_generation_limit = -1
        self.project_limit = -1
        self.export_limit = -1

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'tier': self.tier.value,
            'status': self.status.value,
            'limits': {
                'plan_generation': self.plan_generation_limit,
                'projects': self.project_limit,
                'exports': self.export_limit
            },
            'usage': {
                'plans_generated': self.plans_generated,
                'projects_created': self.projects_created,
                'exports_made': self.exports_made
            },
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None
        }

class Project(Base):
    """Project/Plan storage model"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Project details
    title = Column(String(500), nullable=False)
    description = Column(Text)  # Original user idea
    generated_plan = Column(Text)  # Generated development plan
    reference_urls = Column(JSON)  # List of reference URLs used

    # Metadata
    is_favorite = Column(Boolean, default=False)
    tags = Column(JSON)  # List of tags
    version = Column(Integer, default=1)

    # Generation details
    generation_time_seconds = Column(Float)
    model_used = Column(String(100))
    tokens_used = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="projects")
    exports = relationship("Export", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self, include_plan=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'is_favorite': self.is_favorite,
            'tags': self.tags or [],
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'generation_time': self.generation_time_seconds
        }

        if include_plan:
            data['generated_plan'] = self.generated_plan
            data['reference_urls'] = self.reference_urls or []

        return data

class Export(Base):
    """Export history model"""
    __tablename__ = 'exports'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)

    # Export details
    format = Column(String(20), nullable=False)  # md, docx, pdf, html
    file_path = Column(String(500))
    file_size = Column(Integer)  # bytes

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="exports")

class UsageLog(Base):
    """Usage tracking and analytics"""
    __tablename__ = 'usage_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Action tracking
    action_type = Column(String(50), nullable=False)  # plan_generated, export, project_created, etc.
    action_details = Column(JSON)  # Additional context

    # Resource usage
    processing_time = Column(Float)  # seconds
    tokens_consumed = Column(Integer)
    api_calls_made = Column(Integer, default=1)

    # Success/failure tracking
    success = Column(Boolean, default=True)
    error_message = Column(Text)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_logs")

class SystemSettings(Base):
    """System-wide settings and configuration"""
    __tablename__ = 'system_settings'

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database setup utilities
class Database:
    """Database manager"""

    def __init__(self, db_url: str = "sqlite:///vibedoc.db"):
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

    def drop_all(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(self.engine)

# Pricing configuration
PRICING_TIERS = {
    SubscriptionTier.FREE: {
        'name': 'Free',
        'price': 0,
        'plan_generation_limit': 5,
        'project_limit': 3,
        'export_limit': 10,
        'features': [
            '5 AI-generated plans per month',
            '3 saved projects',
            '10 exports per month',
            'Basic support',
            'All export formats'
        ]
    },
    SubscriptionTier.PRO: {
        'name': 'Pro',
        'price': 19.99,  # USD per month
        'plan_generation_limit': 50,
        'project_limit': 20,
        'export_limit': 200,
        'features': [
            '50 AI-generated plans per month',
            '20 saved projects',
            '200 exports per month',
            'Priority support',
            'Advanced editing features',
            'Custom templates',
            'API access'
        ]
    },
    SubscriptionTier.ENTERPRISE: {
        'name': 'Enterprise',
        'price': 99.99,  # USD per month
        'plan_generation_limit': -1,  # Unlimited
        'project_limit': -1,
        'export_limit': -1,
        'features': [
            'Unlimited AI-generated plans',
            'Unlimited projects',
            'Unlimited exports',
            '24/7 priority support',
            'Team collaboration (coming soon)',
            'Custom AI model fine-tuning',
            'Full API access',
            'SSO integration',
            'Dedicated account manager'
        ]
    }
}
