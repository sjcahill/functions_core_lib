import os
from dotenv import load_dotenv
from functions_core_lib.stripe.client import StripeClient

test_data = {
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

api_key = os.environ.get("STRIPE_TEST_API_KEY")
stripe_client = StripeClient(api_key=api_key)

#
