from __future__ import unicode_literals

from future.builtins import zip

from django import forms
from django.utils.translation import ugettext_lazy as _

from mezzy.utils.forms import UXFormMixin

from ..models import SurveyPurchase, Question


class SurveyPurchaseForm(UXFormMixin, forms.ModelForm):
    """
    Base class inherited by a payment gateway form.
    """
    name = forms.CharField(
        label=_("Name"),
        widget=forms.TextInput(attrs={"placeholder": _("Your Name")}))
    email = forms.CharField(
        label=_("Email"),
        widget=forms.TextInput(attrs={"placeholder": _("Your Email")}))
    purchase_code = forms.CharField(
        label=_("I Have a Code"), required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Enter code")}))

    class Meta:
        model = SurveyPurchase
        fields = ["name", "email"]


class SurveyTakeForm(UXFormMixin, forms.Form):
    """
    Form that an user uses to answer a Survey
    """
    def __init__(self, survey, *args, **kwargs):
        """
        Add each form field to the form
        """
        super(SurveyTakeForm, self).__init__(*args, **kwargs)

        for question in survey.questions.all().order_by("field_type"):
            field_key = "field_%s" % question.id
            field_type = question.field_type

            # Question is a RadioSelect field
            if field_type == Question.RATING_FIELD:
                field = forms.ChoiceField(
                    label=question.prompt,
                    widget=forms.RadioSelect,
                    choices=list(zip(
                        range(1, question.max_rating + 1),
                        range(1, question.max_rating + 1)))
                )
            # Question is a Textarea field
            elif field_type == Question.TEXT_FIELD:
                field = forms.CharField(label=question.prompt, widget=forms.Textarea)

            # Use the HTML5 required attribute
            if question.required:
                field.widget.attrs["required"] = ""
                field.label = '%s*' % unicode(field.label)

            self.fields[field_key] = field
