from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

UUID_RE = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

urlpatterns = [
    url("^purchase/(?P<slug>.*)/$",
        views.SurveyPurchaseCreate.as_view(), name="purchase_create"),
    url("^manage/(?P<public_id>%s)/$" % UUID_RE,
        views.SurveyPurchaseDetail.as_view(), name="purchase_detail"),
    url("^take/(?P<public_id>%s)/$" % UUID_RE,
        views.SurveyResponseCreate.as_view(), name="response_create")
]
