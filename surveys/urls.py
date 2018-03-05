from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

UUID_RE = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

urlpatterns = [
    url("^purchase/(?P<slug>.*)/$",
        views.SurveyPurchaseView.as_view(), name="purchase"),
    url("^manage/(?P<public_id>%s)/$" % UUID_RE,
        views.SurveyManageView.as_view(), name="manage"),
    url("^take/(?P<public_id>%s)/$" % UUID_RE,
        views.SurveyTakeView.as_view(), name="take")
]
