from typing import Optional


class StripeError(Exception):
    """Custom exception for Stripe-related errors"""

    def __init__(self, message: str, stripe_error: Optional[Exception] = None):
        self.message = message
        self.stripe_error = stripe_error
        super().__init__(self.message)
