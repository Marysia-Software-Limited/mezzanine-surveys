# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from copy import deepcopy

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin

from ..models import SurveyPage, Question, SurveyPurchase, SurveyPurchaseCode


survey_fieldsets = [
    (None, {
        "fields": [
            "title", "status", "content", "instructions", "cost", "purchase_response",
            "completed_message",
        ]
    }),
    (_("Report"), {
        "fields": ["report_explanation"]
    }),
    (_("Advanced Options"), {
        "classes": ("collapse-closed",),
        "fields": [("publish_date", "expiry_date")]
    }),
    deepcopy(PageAdmin.fieldsets[-1]),  # Meta panel
]


class SurveyPurchaseCodeInline(TabularDynamicInlineAdmin):
    model = SurveyPurchaseCode


class QuestionInline(TabularDynamicInlineAdmin):
    list_editable = ["_order"]
    model = Question


@admin.register(SurveyPage)
class SurveyPageAdmin(PageAdmin):
    fieldsets = survey_fieldsets
    inlines = [SurveyPurchaseCodeInline, QuestionInline]


@admin.register(SurveyPurchase)
class SurveyPurchaseAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "survey", "transaction_id"]
    search_fields = ["name", "email", "transaction_id"]
