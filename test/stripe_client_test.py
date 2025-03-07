# Then modify your tests to load from .env
import os
import pytest
from functions_core_lib.stripe.client import StripeClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def api_key():
    """Fixture to get the Stripe test API key from environment variables"""
    key = os.environ.get("STRIPE_TEST_API_KEY")
    if not key:
        pytest.skip("STRIPE_TEST_API_KEY environment variable not set")
    return key


@pytest.fixture
def stripe_client(api_key):
    """Fixture to create a StripeClient instance with the test API key"""
    return StripeClient(api_key=api_key)


@pytest.fixture
def test_customer_data():
    """Fixture to provide test customer data"""
    return {
        "email": "test@example.com",
        "company_name": "Test Company",
        "phone": "+15555555555",
        "address": {
            "city": "San Francisco",
            "country": "US",
            "street1": "123 Market St",
            "street2": "Suite 456",
            "zipCode": "94107",
            "state": "CA",
        },
    }


class TestStripeIntegration:
    def test_format_address(self, stripe_client, test_customer_data):
        address = test_customer_data["address"]
        formatted_address = stripe_client.format_address(address)
        assert formatted_address == {
            "city": "San Francisco",
            "country": "US",
            "line1": "123 Market St",
            "line2": "Suite 456",
            "postal_code": "94107",
            "state": "CA",
        }

    def test_create_customer(self, stripe_client, test_customer_data):
        customer_data = test_customer_data
        customer = stripe_client.create_customer(**customer_data)
        assert customer.id is not None

    def test_list_customers(self, stripe_client):
        customers = stripe_client.list_customers()
        print(customers)
        assert isinstance(customers, list)

    # def test_get_customer_by_email(self, stripe_client, test_customer_data):
    #     email = test_customer_data["email"]
    #     customer = stripe_client.get_customer_by_email(email)
    #     print("HEEERRREEE")
    #     print(f"customer is {customer}")
    #     assert customer.get("email") == email
