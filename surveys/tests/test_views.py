from __future__ import absolute_import, unicode_literals

from builtins import range

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from django_dynamic_fixture import get

from mezzanine.core.models import CONTENT_STATUS_DRAFT, CONTENT_STATUS_PUBLISHED

from mezzy.utils.tests import ViewTestMixin

from surveys.models import (
    SurveyPage, SurveyPurchase, SurveyPurchaseCode, SurveyResponse, Question, QuestionResponse)
from surveys.tests import urls_with_surveys
from surveys.views import SurveyPurchaseView, SurveyManageView, SurveyTakeView


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
        data = {}

        # Test invalid purchase code is rejected
        data["purchase_code"] = "invalid"
        self.post(SurveyPurchaseView, slug=self.SURVEY.slug, user=self.USER, data=data)
        self.assertEqual(SurveyPurchase.objects.count(), 0)

        # Test depleted purchase code is rejected
        data["purchase_code"] = depleted_code.code
        self.post(SurveyPurchaseView, slug=self.SURVEY.slug, user=self.USER, data=data)
        self.assertEqual(SurveyPurchase.objects.count(), 0)
        depleted_code.refresh_from_db()
        self.assertEqual(depleted_code.uses_remaining, 0)

        # Test valid code is accepted and purchase is created
        data["purchase_code"] = valid_code.code
        response = self.post(SurveyPurchaseView, slug=self.SURVEY.slug, user=self.USER, data=data)
        purchase = SurveyPurchase.objects.get()
        self.assertEqual(response["location"], purchase.get_absolute_url())
        self.assertEqual(purchase.purchaser, self.USER)
        self.assertEqual(purchase.survey, self.SURVEY)
        self.assertEqual(purchase.transaction_id, valid_code.code)
        self.assertEqual(purchase.payment_method, "Purchase Code")
        self.assertEqual(purchase.amount, 0)

        # Test code uses have been reduced by 1
        valid_code.refresh_from_db()
        self.assertEqual(valid_code.uses_remaining, 9)

    def test_payment(self):
        """
        Purchases completed via the default payment method (doesn't do anything).
        """
        # Test the new purchase was created successfully
        response = self.post(SurveyPurchaseView, slug=self.SURVEY.slug, user=self.USER)
        purchase = SurveyPurchase.objects.get()
        self.assertEqual(response["location"], purchase.get_absolute_url())
        self.assertEqual(purchase.purchaser, self.USER)
        self.assertEqual(purchase.survey, self.SURVEY)
        self.assertEqual(purchase.payment_method, "Demo")
        self.assertEqual(purchase.amount, self.SURVEY.cost)


class SurveyManageTestCase(BaseSurveyPageTest):

    @classmethod
    def setUpTestData(cls):
        super(SurveyManageTestCase, cls).setUpTestData()
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
        response = self.assert200(SurveyManageView, public_id=self.PURCHASE_ID, user=self.USER)
        self.assertEqual(response.context_data["purchase"], self.PURCHASE)


class SurveyTakeTestCase(BaseSurveyPageTest):

    @classmethod
    def setUpTestData(cls):
        super(SurveyTakeTestCase, cls).setUpTestData()
        cls.PURCHASE = get(
            SurveyPurchase, survey=cls.SURVEY, purchaser=cls.USER, purchased_with_code=None,
            report_generated=None)
        cls.PURCHASE_ID = str(cls.PURCHASE.public_id)

    def assertFieldError(self, response, field_key):
        """
        Verify a certain field in a form has an error.
        """
        form = response.context_data["form"]
        try:
            form.errors[field_key]
        except AttributeError:
            self.fail("The form '%s' doesn't contain any errors" % form)
        except KeyError:
            self.fail("The field '%s' doesn't contain any errors" % field_key)

    def test_access(self):
        # Add 5 questions to the survey
        for i in range(0, 5):
            get(Question, survey=self.SURVEY)

        # Anon users can access the survey
        self.assert200(SurveyTakeView, public_id=self.PURCHASE_ID)

        # Logged-in users can access the survey
        response = self.assert200(SurveyTakeView, public_id=self.PURCHASE_ID, user=self.USER)

        # A form is present in the context with our 5 questions
        fields = response.context_data["form"].fields
        self.assertEqual(len(fields), 5)

    def test_survey_response(self):
        """
        Responses to questions in a survey are stored correctly.
        """
        # Create one text and one rating question
        text_question = get(Question, survey=self.SURVEY, field_type=Question.TEXT_FIELD)
        rating_question = get(
            Question, survey=self.SURVEY, field_type=Question.RATING_FIELD, max_rating=5,
            required=True)
        rating_field_key = "question_%s" % rating_question.pk
        data = {"question_%s" % text_question.pk: "TEST"}

        # Required rating question should fail validation if not provided
        data[rating_field_key] = ""
        response = self.post(SurveyTakeView, public_id=self.PURCHASE_ID, data=data)
        self.assertFieldError(response, rating_field_key)
        self.assertEqual(SurveyResponse.objects.count(), 0)

        # Rating question should fail validation if value is above max_rating
        data[rating_field_key] = 10
        response = self.post(SurveyTakeView, public_id=self.PURCHASE_ID, data=data)
        self.assertFieldError(response, rating_field_key)
        self.assertEqual(SurveyResponse.objects.count(), 0)

        # Rating question should fail validation if value is below 1
        data[rating_field_key] = 0
        response = self.post(SurveyTakeView, public_id=self.PURCHASE_ID, data=data)
        self.assertFieldError(response, rating_field_key)
        self.assertEqual(SurveyResponse.objects.count(), 0)

        # Rating question should fail validation if value is not numeric
        data[rating_field_key] = "abcd"
        response = self.post(SurveyTakeView, public_id=self.PURCHASE_ID, data=data)
        self.assertFieldError(response, rating_field_key)
        self.assertEqual(SurveyResponse.objects.count(), 0)

        # Rating question should pass validation if value is correct
        data[rating_field_key] = 3
        self.post(SurveyTakeView, public_id=self.PURCHASE_ID, data=data)
        survey_response = SurveyResponse.objects.get()

        # Verify the rating response was stored correctly
        rating_response = QuestionResponse.objects.get(question=rating_question)
        self.assertEqual(rating_response.rating, 3)
        self.assertEqual(rating_response.text_response, "")
        self.assertEqual(rating_response.response, survey_response)

        # Verify the text response was stored correctly
        text_response = QuestionResponse.objects.get(question=text_question)
        self.assertIsNone(text_response.rating)
        self.assertEqual(text_response.text_response, "TEST")
        self.assertEqual(text_response.response, survey_response)
