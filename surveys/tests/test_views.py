from __future__ import absolute_import, unicode_literals

from copy import copy

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from django_dynamic_fixture import get

from mezzanine.core.models import CONTENT_STATUS_DRAFT, CONTENT_STATUS_PUBLISHED

from mezzy.utils.tests import ViewTestMixin

from surveys.models import SurveyPage, SurveyPurchase, SurveyPurchaseCode
from surveys.tests import urls_with_surveys
from surveys.views import SurveyPurchaseView, SurveyManageView

PURCHASE_DATA = {"name": "Test", "email": "test@test.com"}


class BaseSurveyPageTest(ViewTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super(BaseSurveyPageTest, cls).setUpTestData()
        cls.USER = get(User, is_active=True, is_staff=False)
        cls.SURVEY = SurveyPage.objects.create(cost=10)


@override_settings(ROOT_URLCONF=urls_with_surveys())
class SurveyPurchaseTestCase(BaseSurveyPageTest):

    def test_access(self):
        survey = SurveyPage.objects.create(cost=10)

        # Anon users cannot access surveys
        self.assertLoginRequired(SurveyPurchaseView, slug=survey.slug)

        # Non-published pages cannot be accessed
        survey.status = CONTENT_STATUS_DRAFT
        survey.save()
        self.assert404(SurveyPurchaseView, slug=survey.slug, user=self.USER)

        # Logged in users can access surveys
        survey.status = CONTENT_STATUS_PUBLISHED
        survey.save()
        self.assert200(SurveyPurchaseView, slug=survey.slug, user=self.USER)

    def test_purchase_code(self):
        """
        Purchases completed with purchase codes.
        """
        valid_code = get(SurveyPurchaseCode, survey=self.SURVEY, uses_remaining=10)
        depleted_code = get(SurveyPurchaseCode, survey=self.SURVEY, uses_remaining=0)
        data = copy(PURCHASE_DATA)

        # Test invalid purchase code is rejected
        data["purchase_code"] = "invalid"
        self.post(SurveyPurchaseView, slug=self.SURVEY.slug, user=self.USER, data=data)
        self.assertEqual(SurveyPurchase.objects.count(), 0)

        # Test depleted purchase code is rejected
        data["purchase_code"] = depleted_code.code
        self.post(SurveyPurchaseView, slug=self.SURVEY.slug, user=self.USER, data=data)
        self.assertEqual(SurveyPurchase.objects.count(), 0)

        # Test valid code is accepted
        data["purchase_code"] = valid_code.code
        response = self.post(SurveyPurchaseView, slug=self.SURVEY.slug, user=self.USER, data=data)
        purchase = SurveyPurchase.objects.get()
        self.assertEqual(response["location"], purchase.get_absolute_url())
        self.assertEqual(purchase.purchaser, self.USER)
        self.assertEqual(purchase.survey, self.SURVEY)
        self.assertEqual(purchase.transaction_id, valid_code.code)

        # Test code uses have been reduced by 1
        valid_code.refresh_from_db()
        self.assertEqual(valid_code.uses_remaining, 9)

    def test_payment(self):
        """
        Purchases completed via the default payment method (doesn't do anything).
        """
        data = copy(PURCHASE_DATA)

        # Test the new purchase was created successfully
        response = self.post(SurveyPurchaseView, slug=self.SURVEY.slug, user=self.USER, data=data)
        purchase = SurveyPurchase.objects.get()
        self.assertEqual(response["location"], purchase.get_absolute_url())
        self.assertEqual(purchase.purchaser, self.USER)
        self.assertEqual(purchase.survey, self.SURVEY)
        self.assertEqual(purchase.transaction_id, "--")


class SurveyMangeTestCase(BaseSurveyPageTest):

    @classmethod
    def setUpTestData(cls):
        super(SurveyMangeTestCase, cls).setUpTestData()
        cls.PURCHASE = get(
            SurveyPurchase, survey=cls.SURVEY, purchaser=cls.USER, purchased_with_code=None,
            report_generated=None)
        cls.PURCHASE_ID = str(cls.PURCHASE.public_id)

    def test_access(self):
        # Anon users cannot access the purchase
        self.assertLoginRequired(SurveyManageView, public_id=self.PURCHASE_ID)

        # Non-owner users cannot access the purchase
        random_user = get(User, is_active=True)
        self.assert404(SurveyManageView, public_id=self.PURCHASE_ID, user=random_user)

        # Owner can access the purchase
        self.assert200(SurveyManageView, public_id=self.PURCHASE_ID, user=self.USER)
