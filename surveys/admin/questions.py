# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from ..models import Category, Subcategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ["name", "description"]
    list_display = ["name", "_order"]
    list_editable = ["_order"]


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    fields = ["category", "name", "description"]
    list_display = ["name", "category", "_order"]
    list_editable = ["category", "_order"]
