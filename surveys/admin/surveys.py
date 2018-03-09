# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from copy import deepcopy

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin
from mezzanine.utils.admin import admin_url

from ..models import SurveyPage, Question, SurveyPurchase, SurveyPurchaseCode


surveypage_fieldsets = [
    (None, {
        "fields": ["title", "status", ("publish_date", "expiry_date"), "content"],
    }),
    (_("Purchasing"), {
        "classes": ["collapse-closed"],
        "fields": ["get_purchases_link", "cost", "purchase_response"],
    }),
    (_("Instructions"), {
        "classes": ["collapse-closed"],
        "fields": ["instructions", "completed_message"],
    }),
    (_("Report"), {
        "classes": ["collapse-closed"],
        "fields": ["report_explanation"],
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
    fieldsets = surveypage_fieldsets
    readonly_fields = ["get_purchases_link"]
    inlines = [SurveyPurchaseCodeInline, QuestionInline]

    def get_purchases_link(self, obj):
        if obj.pk is None:
            return ""
        return format_html(
            "<a href='{}?survey__page_ptr__exact={}'>Manage {} purchase(s)</a>",
            admin_url(SurveyPurchase, "changelist"),
            obj.pk,
            obj.purchases.count()
        )
    get_purchases_link.short_description = _("Purchases")


@admin.register(SurveyPurchase)
class SurveyPurchaseAdmin(admin.ModelAdmin):
    list_display = [
        "purchaser", "survey", "amount", "payment_method", "transaction_id", "created"]
    list_filter = ["survey"]
    search_fields = ["purchaser__email", "purchaser__username", "payment_method", "transaction_id"]
    date_hierarchy = "created"

    fieldsets = [
        (None, {
            "fields": [
                "purchaser", "survey", "amount", "payment_method", "transaction_id", "notes",
                "created"]
        }),
        ("Responses", {
            "fields": ["get_public_link", "get_response_count", "report_generated"]
        })
    ]
    readonly_fields = ["created", "get_response_count", "get_public_link"]

    def get_response_count(self, obj):
        return obj.responses.count()
    get_response_count.short_description = _("Responses")

    def get_public_link(self, obj):
        return format_html(
            "<a href='{}' target='_blank'>Open public page</a>",
            obj.get_response_create_url())
    get_public_link.short_description = _("Public link")
