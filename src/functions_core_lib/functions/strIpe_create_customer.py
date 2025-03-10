from functions_core_lib.stripe.stripe_client import StripeClient, StripeError
from functions_core_lib.stripe.types import CustomerApiResponse


def create_customer_function(data: dict, api_key: str) -> CustomerApiResponse:
    """Handler for the create_customer Cloud Function"""
    try:
        client = StripeClient(api_key=api_key)

        # Extract data
        email = data.get("email")
        company_name = data.get("company_name")
        phone = data.get("phone")
        address = data.get("address")

        # Check for existing customer
        response = client.get_customers_by_email(email)  # returns a ListObject where "data" is a list
        customer = response["data"]
        if customer and len(customer) > 0:
            return CustomerApiResponse(
                success=False,
                message=f"Customer with email {email} already exists",
                error_code="CUSTOMER_EXISTS",
                status_code=400,
            )

        # Create customer
        customer = client.create_customer(email, company_name, phone, address)

        return CustomerApiResponse(
            success=True, message="Customer created successfully", data=customer, status_code=201
        )
    except StripeError as e:
        # Handle Stripe errors
        return CustomerApiResponse(success=False, message=str(e), error_code="STRIPE_ERROR", status_code=500)
