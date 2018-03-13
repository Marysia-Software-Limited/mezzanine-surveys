# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.fields import RichTextField
from mezzanine.core.models import Orderable, TimeStamped

from mezzy.utils.models import TitledInline


class Category(TitledInline):
    """
    A Category that contains one or more Subcategories.
    """
    survey = models.ForeignKey(
        "surveys.SurveyPage", on_delete=models.CASCADE, related_name="categories")
    description = RichTextField(_("Description"))

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")


class Subcategory(TitledInline):
    """
    A Subcategory that contains one or more Questions.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    description = RichTextField(_("Description"))

    class Meta:
        verbose_name = _("subcategory")
        verbose_name_plural = _("subcategories")


@python_2_unicode_compatible
class Question(Orderable):
    """
    A question on a SurveyPage.
    """
    RATING_FIELD = 1
    TEXT_FIELD = 2
    QUESTION_TYPES = (
        (RATING_FIELD, "Rating"),
        (TEXT_FIELD, "Text"),
    )

    subcategory = models.ForeignKey(
        Subcategory, on_delete=models.CASCADE, related_name="questions")
    field_type = models.IntegerField(_("Question type"), choices=QUESTION_TYPES)
    prompt = models.CharField(_("Prompt"), max_length=300)
    required = models.BooleanField(_("Required"), default=True)

    def __str__(self):
        return self.prompt

    def clean(self):
        if self.field_type == self.RATING_FIELD and not self.subcategory:
            raise ValidationError(_("A Subcategory is required for rating questions"))


@python_2_unicode_compatible
class SurveyResponse(TimeStamped):
    """
    Collection of all responses related to a Purchase.
    """
    purchase = models.ForeignKey(
        "surveys.SurveyPurchase", related_name="responses", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.created)


@python_2_unicode_compatible
class QuestionResponse(models.Model):
    """
    Response to a single Question.
    """
    response = models.ForeignKey(
        SurveyResponse, related_name="responses", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="responses", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(_("Rating"), blank=True, null=True)
    text_response = models.TextField(_("Text response"), blank=True)

    def __str__(self):
        if self.rating is not None:
            return str(self.rating)
        return self.text_response
