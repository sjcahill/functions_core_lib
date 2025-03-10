import os
import pytest
import time
import uuid

from dotenv import load_dotenv
from functions_core_lib.stripe.stripe_client import StripeClient, format_address
from functions_core_lib.stripe.exceptions import StripeError

# Load environment variables from .env file
load_dotenv()


def generate_unique_email() -> str:
    """Generate a unique email for testing."""
    unique_id = uuid.uuid4().hex[:4]
    return f"test{unique_id}@example.com"


def generate_unique_company_name() -> str:
    """Generate a unique company name for testing."""
    unique_id = uuid.uuid4().hex[:8]
    return f"Test Company {unique_id}"


#########################
# Session-Scoped Fixtures
#########################


@pytest.fixture(scope="session")
def test_api_key():
    """
    Fixture to get the Stripe test API key from environment variables.
    Skips all tests if the key is not set.
    """
    key = os.environ.get("STRIPE_TEST_API_KEY")
    if not key:
        pytest.skip("STRIPE_TEST_API_KEY environment variable not set")
    return key


@pytest.fixture(scope="session")
def stripe_client(test_api_key):
    """Session-scoped fixture to create a single StripeClient."""
    return StripeClient(api_key=test_api_key)


@pytest.fixture(scope="session")
def persistent_customer(stripe_client):
    """
    Creates a single "persistent" test customer once per test session.
    This customer is deleted after all tests have completed.
    """
    customer_data = {
        "email": generate_unique_email(),
        "company_name": "dummy_company",
        "phone": "+15555555555",
        "address": {
            "city": "Test City",
            "country": "US",
            "street1": "123 Test St",
            "street2": "Suite 456",
            "zipCode": "94107",
            "state": "CA",
        },
    }
    # Create the persistent customer
    customer = stripe_client.create_customer(**customer_data)

    yield {
        "id": customer.id,
        "email": customer.email,
        "name": customer.name,
        "phone": customer.phone,
    }

    # Teardown: delete the persistent customer once the entire session is finished
    try:
        stripe_client.delete_customer(customer.id)
    except Exception as e:
        print(f"Warning: Failed to delete persistent test customer {customer.id}: {e}")


#########################
# Function-Scoped Fixtures
#########################


@pytest.fixture
def test_customer_data():
    """Fixture to provide test customer data with a unique email."""
    return {
        "email": generate_unique_email(),
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


@pytest.fixture
def created_customer(stripe_client, test_customer_data):
    """
    Fixture to create a short-lived test customer for each test.
    The customer is cleaned up after the test finishes.
    """
    customer = stripe_client.create_customer(**test_customer_data)
    yield customer
    try:
        stripe_client.delete_customer(customer.id)
    except Exception as e:
        print(f"Warning: Failed to delete test customer {customer.id}: {e}")


#########################
# Utility Tests
#########################


class TestStripeUtils:
    """Tests for the utility functions outside the StripeClient class."""

    def test_format_address(self, test_customer_data):
        """Test that addresses are correctly formatted for Stripe."""
        address = test_customer_data["address"]
        formatted_address = format_address(address)

        assert formatted_address == {
            "city": "San Francisco",
            "country": "US",
            "line1": "123 Market St",
            "line2": "Suite 456",
            "postal_code": "94107",
            "state": "CA",
        }

    def test_format_address_empty(self):
        """Test formatting an empty address."""
        assert format_address(None) == {}
        assert format_address({}) == {}


#########################
# Client Tests
#########################


class TestStripeClient:
    """Tests for the StripeClient class methods."""

    def test_create_customer(self, stripe_client, test_customer_data):
        """Test customer creation."""
        try:
            customer = stripe_client.create_customer(**test_customer_data)

            # Verify the customer was created successfully
            assert customer.id is not None
            assert customer.email == test_customer_data["email"]
            assert customer.name == test_customer_data["company_name"]
            assert customer.phone == test_customer_data["phone"]

            # Clean up
            stripe_client.delete_customer(customer.id)
        except StripeError as e:
            pytest.fail(f"Failed to create customer: {e}")

    def test_get_customer_by_id(self, stripe_client, persistent_customer):
        """
        Test retrieving a customer by ID using the persistent customer.
        This test doesn't create a new customer, using the persistent one instead.
        """
        customer = stripe_client.get_customer_by_id(persistent_customer["id"])

        assert customer.id == persistent_customer["id"]
        assert customer.email == persistent_customer["email"]
        assert customer.name == persistent_customer["name"]

    def test_get_customers_by_email(self, stripe_client, persistent_customer):
        """
        Test retrieving customers by email using the persistent customer.
        """
        # Search for the customer by email
        email = persistent_customer["email"]
        search_result = stripe_client.get_customers_by_email(email)

        # Verify we got a list of results
        assert search_result is not None
        assert hasattr(search_result, "data")
        assert isinstance(search_result["data"], list)

        first_result = search_result["data"][0]
        assert first_result["id"] == persistent_customer["id"]

    def test_update_customer(self, stripe_client, created_customer):
        """Test updating a customer"""
        new_company_name = "Updated Test Company"
        new_phone = "+15551234567"

        updated_customer = stripe_client.update_customer(
            created_customer.id, {"name": new_company_name, "phone": new_phone}
        )

        # Verify the update was successful
        assert updated_customer.id == created_customer.id
        assert updated_customer.name == new_company_name
        assert updated_customer.phone == new_phone
        # Email should remain unchanged
        assert updated_customer.email == created_customer.email

    def test_list_customers(self, stripe_client, persistent_customer):
        """
        Test listing customers with pagination using the persistent customer.
        Ensures our persistent customer appears in the list.
        """
        customers_page = stripe_client.list_customers(limit=100)
        assert hasattr(customers_page, "data")
        assert len(customers_page.data) > 0

        # Check if our persistent customer is in the results
        customer_ids = [c.id for c in customers_page.data]
        assert persistent_customer["id"] in customer_ids

    def test_delete_customer(self, stripe_client, test_customer_data):
        """Test deleting a customer."""
        # Create a customer specifically for this test
        customer = stripe_client.create_customer(**test_customer_data)
        assert customer.id is not None

        # Delete the customer
        result = stripe_client.delete_customer(customer.id)

        # Verify deletion was successful
        assert result.deleted is True
        assert result.id == customer.id

    def test_customer_not_found(self, stripe_client):
        """Test error handling for non-existent customer."""
        non_existent_id = "cus_nonexistent" + uuid.uuid4().hex[:16]

        with pytest.raises(StripeError) as excinfo:
            stripe_client.get_customer_by_id(non_existent_id)

        # Verify the error message contains useful information
        error_message = str(excinfo.value).lower()
        assert "no such customer" in error_message or "could not be found" in error_message
