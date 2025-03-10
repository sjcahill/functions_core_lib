import os
from dotenv import load_dotenv
from functions_core_lib.stripe.stripe_client import StripeClient

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

stripe_client.create_customer(
    email=test_data["email"],
    company_name=test_data["company_name"],
    phone=test_data["phone"],
    address=test_data["address"],
)

good_email = "test@example.com"
resp = stripe_client.get_customers_by_email("poo")
resp
resp["data"][0]["id"]
resp["data"].id
resp[0]
id = resp[0].id
id

type(stripe_client.get_customer_by_id(id))

resp = stripe_client.delete_customer(id)
resp.deleted


customer_id = "cus_RukYh6VpxKr2eP"

params = {"name": "stupid_name"}
resp = stripe_client.update_customer(customer_id, params)
