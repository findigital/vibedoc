"""
Database utilities and helper functions for VibeDoc SaaS
"""

import os
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import func, and_, or_
from models import (
    Database, User, Subscription, Project, Export, UsageLog,
    SystemSettings, SubscriptionTier, SubscriptionStatus,
    PRICING_TIERS
)

logger = logging.getLogger(__name__)

# Initialize database
DB_URL = os.getenv("DATABASE_URL", "sqlite:///vibedoc.db")
db = Database(DB_URL)

def init_database():
    """Initialize database with tables and default data"""
    logger.info("Initializing database...")
    db.init_db()

    # Add default system settings
    session = db.get_session()
    try:
        # Check if settings exist
        existing_settings = session.query(SystemSettings).first()
        if not existing_settings:
            default_settings = [
                SystemSettings(
                    key="maintenance_mode",
                    value={"enabled": False},
                    description="Enable/disable maintenance mode"
                ),
                SystemSettings(
                    key="registration_enabled",
                    value={"enabled": True},
                    description="Enable/disable new user registration"
                ),
                SystemSettings(
                    key="default_tier_limits",
                    value=PRICING_TIERS,
                    description="Default subscription tier limits"
                )
            ]
            session.add_all(default_settings)
            session.commit()
            logger.info("✅ Default system settings created")
        else:
            logger.info("✅ Database already initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        session.rollback()
    finally:
        session.close()

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    session = db.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()

class UserService:
    """User management service"""

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        with get_db_session() as session:
            return session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        with get_db_session() as session:
            return session.query(User).filter(User.email == email).first()

    @staticmethod
    def get_all_users(skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        with get_db_session() as session:
            return session.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user_profile(user_id: int, **kwargs) -> Optional[User]:
        """Update user profile"""
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            allowed_fields = ['full_name', 'email']
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(user, field, value)

            session.commit()
            return user

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete user and all associated data"""
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            session.delete(user)
            session.commit()
            return True

class SubscriptionService:
    """Subscription management service"""

    @staticmethod
    def get_subscription(user_id: int) -> Optional[Subscription]:
        """Get user's subscription"""
        with get_db_session() as session:
            return session.query(Subscription).filter(Subscription.user_id == user_id).first()

    @staticmethod
    def upgrade_subscription(user_id: int, tier: SubscriptionTier, stripe_customer_id: str = None) -> Optional[Subscription]:
        """Upgrade user's subscription tier"""
        with get_db_session() as session:
            subscription = session.query(Subscription).filter(Subscription.user_id == user_id).first()
            if not subscription:
                return None

            # Apply tier limits
            tier_config = PRICING_TIERS.get(tier)
            if not tier_config:
                return None

            subscription.tier = tier
            subscription.plan_generation_limit = tier_config['plan_generation_limit']
            subscription.project_limit = tier_config['project_limit']
            subscription.export_limit = tier_config['export_limit']

            if stripe_customer_id:
                subscription.stripe_customer_id = stripe_customer_id

            subscription.current_period_start = datetime.utcnow()
            subscription.current_period_end = datetime.utcnow() + timedelta(days=30)

            session.commit()
            return subscription

    @staticmethod
    def check_usage_limit(user_id: int, action_type: str) -> tuple[bool, str]:
        """
        Check if user has reached usage limit

        Args:
            user_id: User ID
            action_type: 'plan', 'project', or 'export'

        Returns:
            Tuple[bool, str]: (can_proceed, message)
        """
        with get_db_session() as session:
            subscription = session.query(Subscription).filter(Subscription.user_id == user_id).first()
            if not subscription:
                return False, "No subscription found"

            if action_type == 'plan':
                if subscription.can_generate_plan():
                    return True, "OK"
                return False, f"Monthly limit reached ({subscription.plan_generation_limit} plans). Upgrade to generate more."

            elif action_type == 'project':
                if subscription.can_create_project():
                    return True, "OK"
                return False, f"Project limit reached ({subscription.project_limit} projects). Upgrade for more projects."

            elif action_type == 'export':
                if subscription.can_export():
                    return True, "OK"
                return False, f"Export limit reached ({subscription.export_limit} exports). Upgrade for more exports."

            return False, "Invalid action type"

    @staticmethod
    def increment_usage(user_id: int, action_type: str):
        """Increment usage counter"""
        with get_db_session() as session:
            subscription = session.query(Subscription).filter(Subscription.user_id == user_id).first()
            if not subscription:
                return

            if action_type == 'plan':
                subscription.plans_generated += 1
            elif action_type == 'project':
                subscription.projects_created += 1
            elif action_type == 'export':
                subscription.exports_made += 1

            session.commit()

    @staticmethod
    def reset_monthly_usage_for_all():
        """Reset monthly usage for all subscriptions (run as cron job)"""
        with get_db_session() as session:
            subscriptions = session.query(Subscription).filter(
                Subscription.current_period_end <= datetime.utcnow()
            ).all()

            for sub in subscriptions:
                sub.reset_monthly_usage()
                sub.current_period_start = datetime.utcnow()
                sub.current_period_end = datetime.utcnow() + timedelta(days=30)

            session.commit()
            logger.info(f"✅ Reset usage for {len(subscriptions)} subscriptions")

class ProjectService:
    """Project management service"""

    @staticmethod
    def create_project(user_id: int, title: str, description: str, generated_plan: str,
                      reference_urls: list = None, **kwargs) -> Optional[Project]:
        """Create new project"""
        with get_db_session() as session:
            project = Project(
                user_id=user_id,
                title=title,
                description=description,
                generated_plan=generated_plan,
                reference_urls=reference_urls or [],
                generation_time_seconds=kwargs.get('generation_time'),
                model_used=kwargs.get('model_used'),
                tokens_used=kwargs.get('tokens_used')
            )

            session.add(project)
            session.commit()

            # Increment usage
            SubscriptionService.increment_usage(user_id, 'project')

            return project

    @staticmethod
    def get_user_projects(user_id: int, skip: int = 0, limit: int = 50) -> List[Project]:
        """Get user's projects"""
        with get_db_session() as session:
            return session.query(Project).filter(
                Project.user_id == user_id
            ).order_by(Project.updated_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_project(project_id: int, user_id: int) -> Optional[Project]:
        """Get specific project (with ownership check)"""
        with get_db_session() as session:
            return session.query(Project).filter(
                and_(Project.id == project_id, Project.user_id == user_id)
            ).first()

    @staticmethod
    def update_project(project_id: int, user_id: int, **kwargs) -> Optional[Project]:
        """Update project"""
        with get_db_session() as session:
            project = session.query(Project).filter(
                and_(Project.id == project_id, Project.user_id == user_id)
            ).first()

            if not project:
                return None

            allowed_fields = ['title', 'description', 'generated_plan', 'is_favorite', 'tags']
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(project, field, value)

            project.version += 1
            session.commit()
            return project

    @staticmethod
    def delete_project(project_id: int, user_id: int) -> bool:
        """Delete project"""
        with get_db_session() as session:
            project = session.query(Project).filter(
                and_(Project.id == project_id, Project.user_id == user_id)
            ).first()

            if not project:
                return False

            session.delete(project)
            session.commit()
            return True

    @staticmethod
    def search_projects(user_id: int, query: str) -> List[Project]:
        """Search user's projects"""
        with get_db_session() as session:
            search_pattern = f"%{query}%"
            return session.query(Project).filter(
                and_(
                    Project.user_id == user_id,
                    or_(
                        Project.title.like(search_pattern),
                        Project.description.like(search_pattern)
                    )
                )
            ).all()

class UsageTrackingService:
    """Usage tracking and analytics"""

    @staticmethod
    def log_action(user_id: int, action_type: str, success: bool = True, **kwargs):
        """Log user action"""
        with get_db_session() as session:
            log = UsageLog(
                user_id=user_id,
                action_type=action_type,
                success=success,
                processing_time=kwargs.get('processing_time'),
                tokens_consumed=kwargs.get('tokens_consumed'),
                api_calls_made=kwargs.get('api_calls_made', 1),
                action_details=kwargs.get('details', {}),
                error_message=kwargs.get('error_message')
            )

            session.add(log)
            session.commit()

    @staticmethod
    def get_user_usage_stats(user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get user usage statistics"""
        with get_db_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            logs = session.query(UsageLog).filter(
                and_(
                    UsageLog.user_id == user_id,
                    UsageLog.created_at >= cutoff_date
                )
            ).all()

            stats = {
                'total_actions': len(logs),
                'successful_actions': sum(1 for log in logs if log.success),
                'failed_actions': sum(1 for log in logs if not log.success),
                'total_processing_time': sum(log.processing_time or 0 for log in logs),
                'total_tokens': sum(log.tokens_consumed or 0 for log in logs),
                'actions_by_type': {}
            }

            # Group by action type
            for log in logs:
                action_type = log.action_type
                if action_type not in stats['actions_by_type']:
                    stats['actions_by_type'][action_type] = 0
                stats['actions_by_type'][action_type] += 1

            return stats

    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """Get system-wide statistics"""
        with get_db_session() as session:
            total_users = session.query(func.count(User.id)).scalar()
            active_users = session.query(func.count(User.id)).filter(User.is_active == True).scalar()
            total_projects = session.query(func.count(Project.id)).scalar()

            # Subscription breakdown
            subscription_stats = {}
            for tier in SubscriptionTier:
                count = session.query(func.count(Subscription.id)).filter(
                    Subscription.tier == tier
                ).scalar()
                subscription_stats[tier.value] = count

            return {
                'total_users': total_users,
                'active_users': active_users,
                'total_projects': total_projects,
                'subscription_breakdown': subscription_stats
            }
