
def urls_with_surveys():
    """
    Add our urls to the basic ones provided by Mezzanine.
    project_template is injected in the path by testconf.py.
    """
    from django.conf.urls import include, url
    from project_template.project_name.urls import urlpatterns as base_urls
    surveys_urls = [
        url("^surveys/", include("surveys.urls", namespace="surveys")),
    ]
    return surveys_urls + base_urls
