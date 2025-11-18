"""
Stripe integration service
"""
import stripe
from typing import Optional
from app.core.config import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


async def create_customer(email: str, name: Optional[str] = None) -> stripe.Customer:
    """Create a Stripe customer"""
    return stripe.Customer.create(
        email=email,
        name=name
    )


async def create_checkout_session(
    customer_id: str,
    price_id: str,
    success_url: str,
    cancel_url: str
) -> stripe.checkout.Session:
    """Create a Stripe checkout session"""
    return stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
    )


async def create_portal_session(customer_id: str, return_url: str) -> stripe.billing_portal.Session:
    """Create a Stripe customer portal session"""
    return stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )


async def cancel_subscription(subscription_id: str):
    """Cancel a Stripe subscription"""
    return stripe.Subscription.delete(subscription_id)
