from modeltranslation.decorators import register

from mezzanine.core.translation import (
    TranslatedDisplayable,
    TranslatedRichText,
    TranslatedSlugged,
)

from .models import (
    SurveyPage, SurveyPurchase, SurveyPurchaseCode, Category, Question, SurveyResponse,
    QuestionResponse, Subcategory,
)


@register(SurveyPage)
class SurveyPageTranslationOptions(TranslatedDisplayable, TranslatedRichText, TranslatedSlugged):
    fields = ()


@register(SurveyPurchase)
class SurveyPurchaseTranslationOptions(TranslatedDisplayable, TranslatedRichText, TranslatedSlugged):
    fields = ()


@register(SurveyPurchaseCode)
class SurveyPurchaseCodeTranslationOptions(TranslatedDisplayable, TranslatedRichText, TranslatedSlugged):
    fields = ()


@register(Category)
class CategoryTranslationOptions(TranslatedDisplayable, TranslatedRichText, TranslatedSlugged):
    fields = ()


@register(Question)
class QuestionTranslationOptions(TranslatedDisplayable, TranslatedRichText, TranslatedSlugged):
    fields = ()


@register(SurveyResponse)
class SurveyResponseTranslationOptions(TranslatedDisplayable, TranslatedRichText, TranslatedSlugged):
    fields = ()


@register(QuestionResponse)
class QuestionResponseTranslationOptions(TranslatedDisplayable, TranslatedRichText, TranslatedSlugged):
    fields = ()


@register(Subcategory)
class SubcategoryTranslationOptions(TranslatedDisplayable, TranslatedRichText, TranslatedSlugged):
    fields = ()

