import stripe
from typing import Optional

from stripe import Customer, ListObject, PaymentMethod

from functions_core_lib.stripe.exceptions import StripeError
from functions_core_lib.stripe.types import AddressDict, StripeAddressDict
from functions_core_lib.stripe.logger import core_logger


def format_address(address: Optional[AddressDict]) -> StripeAddressDict:
    """
    Format address from application format to Stripe format.

    Args:
        address: Dictionary containing address details in application format

    Returns:
        Dictionary with address details formatted for Stripe API
    """
    if not address:
        return {}

    core_logger.info(f"Formatting address: {address}")

    # Field mapping from flutter app to what stripe wants
    field_mapping = {
        "city": "city",
        "country": "country",
        "street1": "line1",
        "street2": "line2",  # Fixed typo here
        "zipCode": "postal_code",
        "state": "state",
    }

    return {
        field_mapping[k]: v for k, v in address.items() if k in field_mapping and v
    }  # Only include non-empty values


class StripeClient:
    def __init__(self, api_key: str):
        """
        Initialize a Stripe client with the given API key.

        Args:
            api_key: The Stripe API key to use for all operations
        """
        self.api_key = api_key
        # Initialize a client instance instead of setting global API key
        self.stripe = stripe.StripeClient(api_key)

    ########################
    # Create Methods
    ########################
    def create_customer(
        self, email: str, company_name: str, phone: str, address: Optional[AddressDict] = None
    ) -> Customer:
        """
        Creates a new Stripe customer with the provided information.

        Args:
            email: Customer's email address
            company_name: Name of the customer's company
            phone: Customer's phone number
            address: Dictionary containing address details

        Returns:
            Stripe customer object

        Raises:
            StripeError: If the customer creation fails
        """
        stripe_address = format_address(address)
        params = {
            "email": email,
            "name": company_name,
            "phone": phone,
        }

        # Only add address if it's not empty
        if stripe_address:
            params["address"] = stripe_address
        core_logger.info(f"Creating Stripe customer with params: {params}")

        try:
            return self.stripe.customers.create(params)
        except Exception as e:
            error_msg = f"Error when creating Stripe customer: {e}"
            raise StripeError(error_msg, e)

    ########################
    # Read Methods
    ########################

    def get_customer_by_id(self, customer_id: str) -> Customer:
        """
        Retrieve a customer by their Stripe ID.

        Args:
            customer_id: The Stripe customer ID

        Returns:
            Stripe customer object

        Raises:
            StripeError: If the customer retrieval fails
        """
        core_logger.info(f"Retrieving Stripe customer with ID {customer_id}")
        try:
            return self.stripe.customers.retrieve(customer_id)
        except Exception as e:
            error_msg = f"Error when retrieving Stripe customer {customer_id}: {e}"
            raise StripeError(error_msg, e)

    def get_customers_by_email(self, email: str) -> ListObject[Customer]:
        """
        Find customers by email address.

        Args:
            email: The email address to search for

        Returns:
            List of matching Stripe customer objects

        Raises:
            StripeError: If the search fails
        """
        core_logger.info(f"Searching for Stripe customers with email {email}")

        params = {
            "limit": 1,
            "email": email,
        }

        try:
            return self.stripe.customers.list(params)
        except Exception as e:
            error_msg = f"Error when searching for Stripe customers with email {email}: {e}"
            raise StripeError(error_msg, e)

    def list_customers(self, limit: int = 100, starting_after: Optional[str] = None) -> ListObject[Customer]:
        """
        List Stripe customers with pagination support.

        Args:
            limit: Maximum number of customers to return (default 100, max 100)
            starting_after: Cursor for pagination (customer ID to start after)

        Returns:
            Paginated list of Stripe customer objects

        Raises:
            StripeError: If listing customers fails
        """
        core_logger.info(f"Listing Stripe customers with limit {limit} and starting_after {starting_after}")

        params = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after

        try:
            return self.stripe.customers.list(params)
        except Exception as e:
            error_msg = f"Error when listing Stripe customers: {e}"
            raise StripeError(error_msg, e)

    ########################
    # Update Methods
    ########################

    def update_customer(self, customer_id: str, update_params) -> Customer:
        """
        Update an existing Stripe customer.

        Args:
            customer_id: The Stripe customer ID
            **update_params: Parameters to update on the customer

        Returns:
            Updated Stripe customer object

        Raises:
            StripeError: If the customer update fails
        """
        core_logger.info(f"Updating Stripe customer {customer_id} with params: {update_params}")

        try:
            return self.stripe.customers.update(customer_id, update_params)
        except Exception as e:
            error_msg = f"Error when updating Stripe customer {customer_id}: {e}"
            raise StripeError(error_msg, e)

    # Additional payment method management
    def attach_payment_method(self, payment_method_id: str, customer_id: str) -> PaymentMethod:
        """
        Attach a payment method to a customer.

        Args:
            payment_method_id: The Stripe payment method ID
            customer_id: The Stripe customer ID

        Returns:
            Stripe payment method object

        Raises:
            StripeError: If attaching the payment method fails
        """
        core_logger.info(f"Attaching payment method {payment_method_id} to customer {customer_id}")

        try:
            return self.stripe.payment_methods.attach(payment_method_id, customer=customer_id)
        except Exception as e:
            error_msg = f"Error attaching payment method {payment_method_id} to customer {customer_id}: {e}"
            raise StripeError(error_msg, e)

    ########################
    # Delete Methods
    ########################

    def delete_customer(self, customer_id: str) -> Customer:
        """
        Delete a Stripe customer.

        Args:
            customer_id: The Stripe customer ID

        Returns:
            Deletion confirmation from Stripe

        Raises:
            StripeError: If the customer deletion fails
        """
        core_logger.info(f"Deleting Stripe customer with ID {customer_id}")

        try:
            return self.stripe.customers.delete(customer_id)
        except Exception as e:
            error_msg = f"Error when deleting Stripe customer {customer_id}: {e}"
            raise StripeError(error_msg, e)
