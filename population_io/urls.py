from django.conf.urls import patterns, include, url
from django.http.response import HttpResponse
import api.urls


API_VERSION_PREFIX = r'^1.0/'


# FIXME: hack to make the swagger-ui index.html be served from /
def docs_index(request):
    with open('static/swagger-ui/index.html', 'r') as index:
        return HttpResponse(index.read())


urlpatterns = patterns('',
    # /1.0/ (API)
    url(API_VERSION_PREFIX, include(api.urls)),

    # / (Swagger documentation)
    url(r'^$', docs_index),
)
