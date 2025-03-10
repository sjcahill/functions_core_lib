from functions_core_lib.stripe.stripe_client import StripeClient, StripeError
from functions_core_lib.stripe.types import CustomerApiResponse


def delete_customer_by_email_function(data: dict, api_key: str) -> CustomerApiResponse:
    """Handler for the create_customer Cloud Function"""
    try:
        client = StripeClient(api_key=api_key)

        # Extract email from customer
        email = data.get("email")

        if not email:
            return CustomerApiResponse(
                success=False, message="Email is required for deleting a customer", status_code=400
            )

        resp = client.get_customers_by_email(email)  # returns a ListObject where "data" is a list
        customer = resp["data"]

        if customer and len(customer) > 0:
            customer_id = customer["id"]
            response = client.delete_customer(customer_id)
            if response.deleted:
                return CustomerApiResponse(
                    success=True, message=f"Customer with email {email} deleted successfully", status_code=200
                )
            else:
                return CustomerApiResponse(
                    success=False, message=f"Customer with email {email} could not be deleted", status_code=500
                )
    except StripeError as e:
        # Handle Stripe errors
        return CustomerApiResponse(success=False, message=str(e), error_code="STRIPE_ERROR", status_code=500)
