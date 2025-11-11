"""
VibeDoc SaaS Initialization Script
Sets up database and creates admin user
"""

import sys
import logging
from getpass import getpass
from database import init_database, get_db_session
from auth import AuthService
from models import SubscriptionTier

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    """Initialize SaaS database and create admin user"""

    logger.info("=" * 60)
    logger.info("🚀 VibeDoc SaaS Initialization")
    logger.info("=" * 60)

    # Step 1: Initialize database
    logger.info("\n📦 Step 1: Initializing database...")
    try:
        init_database()
        logger.info("✅ Database initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)

    # Step 2: Create admin user
    logger.info("\n👤 Step 2: Create admin user")
    logger.info("-" * 60)

    # Get admin details
    print("\nEnter admin user details:")
    email = input("Email: ").strip()
    username = input("Username: ").strip()
    full_name = input("Full Name: ").strip()

    # Get password with confirmation
    while True:
        password = getpass("Password (min 8 characters): ")
        password_confirm = getpass("Confirm Password: ")

        if password != password_confirm:
            logger.warning("❌ Passwords do not match. Try again.")
            continue

        if len(password) < 8:
            logger.warning("❌ Password must be at least 8 characters. Try again.")
            continue

        break

    # Create admin user
    try:
        with get_db_session() as session:
            auth_service = AuthService(session)

            success, message, user = auth_service.register_user(
                email=email,
                username=username,
                password=password,
                full_name=full_name
            )

            if not success:
                logger.error(f"❌ Failed to create admin user: {message}")
                sys.exit(1)

            # Set as admin
            user.is_admin = True
            user.email_verified = True

            # Upgrade to Enterprise tier
            from database import SubscriptionService
            SubscriptionService.upgrade_subscription(user.id, SubscriptionTier.ENTERPRISE)

            session.commit()

            logger.info(f"\n✅ Admin user created successfully!")
            logger.info(f"   Email: {user.email}")
            logger.info(f"   Username: {user.username}")
            logger.info(f"   API Key: {user.api_key}")
            logger.info(f"   Tier: ENTERPRISE (unlimited)")

    except Exception as e:
        logger.error(f"❌ Failed to create admin user: {e}")
        sys.exit(1)

    # Step 3: Create sample users (optional)
    logger.info("\n📝 Step 3: Create sample users (optional)")
    create_samples = input("Create sample users for testing? (y/N): ").strip().lower()

    if create_samples == 'y':
        logger.info("\n Creating sample users...")

        sample_users = [
            {
                'email': 'free@example.com',
                'username': 'free_user',
                'password': 'password123',
                'full_name': 'Free User',
                'tier': SubscriptionTier.FREE
            },
            {
                'email': 'pro@example.com',
                'username': 'pro_user',
                'password': 'password123',
                'full_name': 'Pro User',
                'tier': SubscriptionTier.PRO
            }
        ]

        with get_db_session() as session:
            auth_service = AuthService(session)

            for sample in sample_users:
                tier = sample.pop('tier')

                success, message, user = auth_service.register_user(**sample)

                if success:
                    user.email_verified = True

                    # Upgrade tier if needed
                    if tier != SubscriptionTier.FREE:
                        from database import SubscriptionService
                        SubscriptionService.upgrade_subscription(user.id, tier)

                    session.commit()

                    logger.info(f"   ✅ Created {tier.value} user: {user.username}")
                else:
                    logger.warning(f"   ⚠️ Failed to create {sample['username']}: {message}")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("🎉 VibeDoc SaaS initialization complete!")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("1. Start the SaaS app: python saas_app.py")
    logger.info("2. Start the API server: python api.py")
    logger.info("3. Configure Stripe keys in .env for payments")
    logger.info("\n✨ Happy building with VibeDoc!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n❌ Initialization cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
