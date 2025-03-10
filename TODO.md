I need a main method per cloud function

so create_stripe_customer(), delete_stripe_customer(), etc.

These are all I am going to be calling in my cloud functions and I will handle
all the implementation details and checking within this library so that I can test it
all.

The only things my functions will have to do is to retrieve the secret and essentially
"wrap" the API requests.

I also want to keep my functions as limited as possible and add to them only when needed.

Right now I just need to be able to literally create, read, update and delete customers