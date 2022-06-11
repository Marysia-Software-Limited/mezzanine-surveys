# Mezzanine Surveys

Surveying and reporting package for Mezzanine CMS:

- Admin users create a page of type "Survey Page". This allows them to define the essential survey information and the questions related to it.
- Regular users can access that page and buy the survey via purchase code or credit card (payment processors are customizable and extensible).
- When users purchase a survey, they will gain access to the Survey Purchase dashboard, where they can get the public link and share it with their contacts.
- With the public link anyone can answer the Survey, and their Survey Response will be stored on the site.
- Once the purchaser gets all the Responses they need, they can close the Survey and generate a report (downloadable as PDF).

Additionally, admin users can control the Categories, Subcategories, and Purchases from the admin interface under the "Surveys" section of the sidebar.

## Installation

1. Install from pip: `pip install mezzanine-surveys`.

1. Add `"surveys"` to `settings.INSTALLED_APPS`.

1. Include `"surveys.urls"` before Mezzanine's catch-all patterns in `urls.py`:

    ```python
    path("surveys/", include("surveys.urls", namespace="surveys")),
    ```
    You can also replace `surveys/` with any other prefix you prefer.

1. Run `python manage.py migrate` to create all tables.

## Payment Gateways

By default Mezzanine Surveys will allow anyone to purchase a survey without providing payment information (all Survey Purchases will have their transaction ID set to "Complimentary"). If you plan to require payment to access a survey, use one of the following payment gateways:

### Authorize.net

First, install the `py-authorize` package: `pip install py-authorize`.

Then add your credentials to your settings module and configure the purchase view:

```python
AUTHORIZE_NET_LOGIN = "<your login>"
AUTHORIZE_NET_TRANS_KEY = "<your key>"
AUTHORIZE_NET_TEST_MODE = True  # Set to False in production

SURVEYS_PURCHASE_CREATE_VIEW = "surveys.payments.authorizenet.AuthorizenetSurveyPurchaseCreate"
```

That's it! Now when the user visits the purchase page, they will see fields to enter their credit card information and have it processed by Authorize.net. Survey Purchases will now store the transaction ID for future reference.
