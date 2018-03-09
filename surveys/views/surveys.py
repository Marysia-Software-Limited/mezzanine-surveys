from __future__ import absolute_import, unicode_literals

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from mezzy.utils.views import LoginRequiredMixin, FormMessagesMixin

from ..forms.surveys import SurveyPurchaseForm, SurveyResponseForm
from ..models import SurveyPage, SurveyPurchase, SurveyPurchaseCode


class SurveyPurchaseView(LoginRequiredMixin, FormMessagesMixin, generic.CreateView):
    """
    Handles payment process for buying a survey.
    """
    form_class = SurveyPurchaseForm
    template_name = "surveys/survey_purchase.html"
    success_message = _("You have successfully purchased this survey")
    error_message = _("There was a problem with the payment process. Please try again.")

    @cached_property
    def survey(self):
        return get_object_or_404(
            SurveyPage.objects.published(for_user=self.request.user),
            slug=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        kwargs.update({
            "survey": self.survey,
        })
        return super(SurveyPurchaseView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        """
        The form is valid, let's process the payment and save the purchase.
        """
        form.instance.survey = self.survey
        form.instance.purchaser = self.request.user

        # Process via purchase code or regular payment
        purchase_code = form.cleaned_data.get("purchase_code")
        try:
            if purchase_code:
                self.process_purchase_code(purchase_code, form)
            else:
                self.process_payment(form)
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)

        # Code or payment processed successfully, save and continue
        return super(SurveyPurchaseView, self).form_valid(form)

    def process_purchase_code(self, purchase_code, form):
        """
        Process a purchase based on code entered by the user.
        """
        try:
            code = self.survey.purchase_codes.get(code=purchase_code, uses_remaining__gt=0)
        except SurveyPurchaseCode.DoesNotExist:
            raise ValidationError(_("The code you entered is not valid"))

        code.uses_remaining = F("uses_remaining") - 1
        try:
            code.save()
        except IntegrityError:  # Raised when uses_remaining becomes negative
            raise ValidationError(_("The code you entered is no longer available"))

        form.instance.amount = 0
        form.instance.transaction_id = purchase_code
        form.instance.payment_method = "Purchase Code"

    def process_payment(self, form):
        """
        Process the payment.
        Sets the charge details and transaction ID for the SurveyPurchase.
        """
        form.instance.transaction_id = "--"
        form.instance.payment_method = "Demo"
        form.instance.amount = form.instance.survey.cost


class SurveyManageView(LoginRequiredMixin, generic.TemplateView):
    """
    Overview of survey that provides a report generation functionality.
    """
    template_name = "surveys/survey_manage.html"

    @cached_property
    def purchase(self):
        return get_object_or_404(
            SurveyPurchase.objects.select_related("survey"),
            public_id=self.kwargs["public_id"], purchaser=self.request.user)

    def get_context_data(self, **kwargs):
        kwargs.update({
            "purchase": self.purchase,
            "survey": self.purchase.survey,
        })
        return super(SurveyManageView, self).get_context_data(**kwargs)


class SurveyTakeView(FormMessagesMixin, generic.CreateView):
    """
    Allows a user to answer a survey and submit it.
    """
    form_class = SurveyResponseForm
    template_name = "surveys/survey_take.html"
    success_message = "Thank you! Your responses have been saved successfully"

    @cached_property
    def purchase(self):
        return get_object_or_404(
            SurveyPurchase.objects.select_related("survey").prefetch_related("survey__questions"),
            public_id=self.kwargs["public_id"])

    def get_form_kwargs(self):
        kwargs = super(SurveyTakeView, self).get_form_kwargs()
        kwargs.update({
            "purchase": self.purchase
        })
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs.update({
            "survey": self.purchase.survey,
        })
        return super(SurveyTakeView, self).get_context_data(**kwargs)

    def get_success_url(self):
        return "/"
