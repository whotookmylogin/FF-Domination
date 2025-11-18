"""
Billing and Stripe endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import stripe

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from app.models.user import User, SubscriptionTier
from app.services.stripe_service import create_checkout_session, create_portal_session

router = APIRouter()


class CheckoutSessionRequest(BaseModel):
    """Request to create checkout session"""
    tier: str  # pro or champion


class CheckoutSessionResponse(BaseModel):
    """Response with checkout session URL"""
    session_id: str
    url: str


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout(
    request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a Stripe checkout session"""

    # Price IDs (these would be set up in Stripe dashboard)
    price_ids = {
        "pro": "price_pro_monthly",  # Replace with actual Stripe price ID
        "champion": "price_champion_monthly"  # Replace with actual Stripe price ID
    }

    if request.tier not in price_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tier"
        )

    # Create or get Stripe customer
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.name
        )
        current_user.stripe_customer_id = customer.id
        await db.commit()

    # Create checkout session
    session = await create_checkout_session(
        customer_id=current_user.stripe_customer_id,
        price_id=price_ids[request.tier],
        success_url="http://localhost:3000/dashboard?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://localhost:3000/pricing"
    )

    return {"session_id": session.id, "url": session.url}


@router.post("/create-portal-session")
async def create_portal(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a Stripe customer portal session"""

    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer found"
        )

    session = await create_portal_session(
        customer_id=current_user.stripe_customer_id,
        return_url="http://localhost:3000/dashboard/settings"
    )

    return {"url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events"""

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle different event types
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Update user subscription
        customer_id = session["customer"]
        subscription_id = session["subscription"]

        # Find user by Stripe customer ID
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.stripe_subscription_id = subscription_id
            # Determine tier from price ID
            # This is simplified - in production, check the actual price ID
            user.subscription_tier = SubscriptionTier.PRO
            await db.commit()

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]

        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.subscription_tier = SubscriptionTier.FREE
            user.stripe_subscription_id = None
            await db.commit()

    return {"status": "success"}
