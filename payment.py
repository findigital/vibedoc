"""
Payment processing integration for VibeDoc SaaS
Stripe integration for subscription management
"""

import os
import logging
from typing import Optional, Dict, Tuple
import stripe
from datetime import datetime, timedelta
from models import SubscriptionTier, PRICING_TIERS
from database import SubscriptionService

logger = logging.getLogger(__name__)

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Stripe Price IDs (set these in your Stripe dashboard)
STRIPE_PRICE_IDS = {
    SubscriptionTier.PRO: os.getenv("STRIPE_PRICE_ID_PRO", "price_pro_monthly"),
    SubscriptionTier.ENTERPRISE: os.getenv("STRIPE_PRICE_ID_ENTERPRISE", "price_enterprise_monthly")
}

class PaymentError(Exception):
    """Payment processing error"""
    pass

class PaymentService:
    """Stripe payment service"""

    @staticmethod
    def create_customer(email: str, name: str, user_id: int) -> Tuple[bool, str, Optional[str]]:
        """
        Create Stripe customer

        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, customer_id)
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={'user_id': user_id}
            )

            logger.info(f"✅ Created Stripe customer {customer.id} for user {user_id}")
            return True, "Customer created", customer.id

        except stripe.error.StripeError as e:
            logger.error(f"❌ Stripe customer creation failed: {e}")
            return False, str(e), None

    @staticmethod
    def create_checkout_session(
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        user_id: int
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Create Stripe Checkout session for subscription

        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, checkout_url)
        """
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={'user_id': user_id}
            )

            logger.info(f"✅ Created checkout session {session.id} for user {user_id}")
            return True, "Checkout session created", session.url

        except stripe.error.StripeError as e:
            logger.error(f"❌ Checkout session creation failed: {e}")
            return False, str(e), None

    @staticmethod
    def create_subscription(
        user_id: int,
        tier: SubscriptionTier,
        success_url: str,
        cancel_url: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Create subscription checkout session

        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, checkout_url)
        """
        if tier not in STRIPE_PRICE_IDS:
            return False, "Invalid subscription tier", None

        # Get or create Stripe customer
        subscription = SubscriptionService.get_subscription(user_id)
        if not subscription:
            return False, "User subscription not found", None

        customer_id = subscription.stripe_customer_id

        if not customer_id:
            # Create Stripe customer
            from database import UserService
            user = UserService.get_user_by_id(user_id)
            if not user:
                return False, "User not found", None

            success, message, customer_id = PaymentService.create_customer(
                user.email,
                user.full_name or user.username,
                user_id
            )

            if not success:
                return False, message, None

            # Update subscription with customer ID
            subscription.stripe_customer_id = customer_id

        # Create checkout session
        price_id = STRIPE_PRICE_IDS[tier]
        return PaymentService.create_checkout_session(
            customer_id,
            price_id,
            success_url,
            cancel_url,
            user_id
        )

    @staticmethod
    def cancel_subscription(subscription_id: str) -> Tuple[bool, str]:
        """
        Cancel Stripe subscription

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            stripe.Subscription.delete(subscription_id)
            logger.info(f"✅ Cancelled subscription {subscription_id}")
            return True, "Subscription cancelled"

        except stripe.error.StripeError as e:
            logger.error(f"❌ Subscription cancellation failed: {e}")
            return False, str(e)

    @staticmethod
    def update_subscription_tier(subscription_id: str, new_price_id: str) -> Tuple[bool, str]:
        """
        Update subscription to new tier

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': new_price_id,
                }],
                proration_behavior='always_invoice'
            )

            logger.info(f"✅ Updated subscription {subscription_id} to price {new_price_id}")
            return True, "Subscription updated"

        except stripe.error.StripeError as e:
            logger.error(f"❌ Subscription update failed: {e}")
            return False, str(e)

    @staticmethod
    def handle_webhook(payload: bytes, sig_header: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Handle Stripe webhook events

        Returns:
            Tuple[bool, str, Optional[Dict]]: (success, message, event_data)
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )

            logger.info(f"📨 Received Stripe webhook: {event['type']}")

            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                return PaymentService._handle_checkout_completed(session)

            elif event['type'] == 'customer.subscription.created':
                subscription = event['data']['object']
                return PaymentService._handle_subscription_created(subscription)

            elif event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                return PaymentService._handle_subscription_updated(subscription)

            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                return PaymentService._handle_subscription_deleted(subscription)

            elif event['type'] == 'invoice.payment_succeeded':
                invoice = event['data']['object']
                return PaymentService._handle_payment_succeeded(invoice)

            elif event['type'] == 'invoice.payment_failed':
                invoice = event['data']['object']
                return PaymentService._handle_payment_failed(invoice)

            return True, f"Unhandled event type: {event['type']}", None

        except stripe.error.SignatureVerificationError as e:
            logger.error(f"❌ Webhook signature verification failed: {e}")
            return False, "Invalid signature", None

        except Exception as e:
            logger.error(f"❌ Webhook processing error: {e}")
            return False, str(e), None

    @staticmethod
    def _handle_checkout_completed(session: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """Handle successful checkout"""
        user_id = int(session['metadata'].get('user_id', 0))
        subscription_id = session.get('subscription')

        if not user_id:
            return False, "Missing user_id in metadata", None

        # Update user's subscription
        subscription = SubscriptionService.get_subscription(user_id)
        if subscription:
            subscription.stripe_subscription_id = subscription_id

        logger.info(f"✅ Checkout completed for user {user_id}")
        return True, "Checkout completed", {'user_id': user_id, 'subscription_id': subscription_id}

    @staticmethod
    def _handle_subscription_created(stripe_subscription: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """Handle subscription creation"""
        user_id = int(stripe_subscription['metadata'].get('user_id', 0))

        if not user_id:
            return False, "Missing user_id", None

        # Determine tier based on price
        price_id = stripe_subscription['items']['data'][0]['price']['id']
        tier = None

        for t, pid in STRIPE_PRICE_IDS.items():
            if pid == price_id:
                tier = t
                break

        if tier:
            SubscriptionService.upgrade_subscription(
                user_id,
                tier,
                stripe_subscription['customer']
            )
            logger.info(f"✅ Subscription created for user {user_id}, tier: {tier.value}")

        return True, "Subscription created", {'user_id': user_id, 'tier': tier.value if tier else None}

    @staticmethod
    def _handle_subscription_updated(stripe_subscription: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """Handle subscription update"""
        logger.info(f"Subscription updated: {stripe_subscription['id']}")
        return True, "Subscription updated", None

    @staticmethod
    def _handle_subscription_deleted(stripe_subscription: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """Handle subscription cancellation"""
        user_id = int(stripe_subscription['metadata'].get('user_id', 0))

        if user_id:
            # Downgrade to free tier
            SubscriptionService.upgrade_subscription(user_id, SubscriptionTier.FREE)
            logger.info(f"✅ Subscription cancelled for user {user_id}, downgraded to FREE")

        return True, "Subscription cancelled", {'user_id': user_id}

    @staticmethod
    def _handle_payment_succeeded(invoice: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """Handle successful payment"""
        logger.info(f"Payment succeeded: {invoice['id']}")
        return True, "Payment succeeded", None

    @staticmethod
    def _handle_payment_failed(invoice: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """Handle failed payment"""
        logger.warning(f"Payment failed: {invoice['id']}")
        return True, "Payment failed", None

    @staticmethod
    def get_customer_portal_url(customer_id: str, return_url: str) -> Tuple[bool, str, Optional[str]]:
        """
        Create Stripe Customer Portal session

        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, portal_url)
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )

            return True, "Portal session created", session.url

        except stripe.error.StripeError as e:
            logger.error(f"❌ Customer portal creation failed: {e}")
            return False, str(e), None
