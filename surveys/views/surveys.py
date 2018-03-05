from __future__ import absolute_import, unicode_literals

from django.db.models import Count
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from mezzy.utils.views import LoginRequiredMixin

from ..forms.surveys import SurveyPurchaseForm, SurveyTakeForm
from ..models import Question, QuestionResponse, SurveyPage, SurveyPurchase, SurveyPurchaseCode


class SurveyPurchaseView(LoginRequiredMixin, generic.CreateView):
    """
    Handles payment process for buying a survey.
    """
    form_class = SurveyPurchaseForm
    template_name = "surveys/survey_purchase.html"
    success_message = _("You have successully purchased this survey.")
    error_message = _("There was a problem with the payment process. Please try again.")

    @cached_property
    def survey(self):
        return get_object_or_404(SurveyPage, slug=self.kwargs["slug"])

    def form_valid(self, form):
        """
        The form is valid, let's save the order, collect payment and send a confirmation email.
        Any ValidationErrors raised by process_payment() will be attached back to the form.
        """
        purchase = form.save(commit=False)

        # Assume a user is "claiming" a purchase if they're paying for it
        purchase.purchaser = self.request.user

        # Case 1: Check first for purchase codes
        code = form.cleaned_data.get("purchase_code")
        if code:
            try:
                code = self.survey.purchase_codes.get(
                    code=code, uses_remaining__gte=1)
            except SurveyPurchaseCode.DoesNotExist:
                form.add_error(None, _("The code you entered is not valid"))
                return self.form_invalid(form)
            else:
                code.uses_remaining -= 1
                code.save()
                purchase.purchased_with_code = code
                purchase.transaction_id = code.code
                purchase.charge_details = _("Survey purchased using code %s" % code.code)
        # Case 2: Call a payment provider
        else:
            try:
                self.process_payment(purchase)
            except ValidationError as error:
                form.add_error(None, error)
                return self.form_invalid(form)

        # The payment process was performed, save the SurveyPurchase
        purchase.survey = self.survey
        purchase.save()

        messages.success(self.request, self.success_message, fail_silently=True)
        return redirect(purchase.get_absolute_url())

    def process_payment(self, purchase):
        """
        Process the payment.
        Sets the charge details and transaction ID for the SurveyPurchase.
        Errors will be raised as ValidationError and handled by form_valid().
        """
        purchase.charge_details = _("Free survey")
        purchase.transaction_id = "--"
        purchase.charge_details = _("Survey cost: $%s" % self.survey.cost)


class SurveyManageView(LoginRequiredMixin, generic.DetailView):
    """
    Overview of survey that provides a report generation functionality.
    """
    model = SurveyPurchase
    template_name = "surveys/survey_manage.html"

    @cached_property
    def purchase(self):
        return get_object_or_404(
            SurveyPurchase.objects.select_related("survey"), public_id=self.kwargs["public_id"])

    @cached_property
    def survey(self):
        return self.purchase.survey

    def get_object(self):
        return self.purchase

    def get_num_responses(self):
        return self.survey.questions.aggregate(Count("responses")).get("responses__count")

    def get_context_data(self, **kwargs):
        context = super(SurveyManageView, self).get_context_data(**kwargs)

        context.update({
            "purchase": self.purchase,
            "survey": self.survey,
            "num_of_responses": self.get_num_responses(),
        })
        return context


class SurveyTakeView(generic.FormView):
    """
    Allows a user to answer a survey and submit it.
    """
    form_class = SurveyTakeForm
    template_name = "surveys/survey_take.html"

    @cached_property
    def purchase(self):
        return get_object_or_404(
            SurveyPurchase.objects.select_related("survey").prefetch_related("survey__questions"),
            public_id=self.kwargs["public_id"])

    @cached_property
    def survey(self):
        return self.purchase.survey

    def get_form_kwargs(self):
        kwargs = super(SurveyTakeView, self).get_form_kwargs()
        kwargs.update({
            "survey": self.survey
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SurveyTakeView, self).get_context_data(**kwargs)
        context.update({
            "survey": self.survey,
        })
        return context

    def form_valid(self, form):
        # Create responses for every question
        for question in self.survey.questions.all():
            response = QuestionResponse(question=question)

            field_type = question.field_type
            field = form.cleaned_data.get("field_%s" % question.id)
            if field_type == Question.RATING_FIELD:
                response.rating = field
            elif field_type == Question.TEXT_FIELD:
                response.text_response = field

            response.save()

        return redirect(reverse("home"))
