from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url

SURVEYS_URLCONF = [
    url("^surveys/", include("surveys.urls", namespace="surveys")),
]
