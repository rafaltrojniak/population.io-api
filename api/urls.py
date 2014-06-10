from django.conf.urls import patterns, include, url
from django.conf import settings
from api import views



API_VERSION_PREFIX = r'1.0/'
WP_RANK_PREFIX = r'wp-rank/'
PERSON_PATH = r'(?P<dob>.+)/(?P<sex>.+)/(?P<country>.+)/'


urlpatterns = [
    # /api/1.0/countries/
    url(API_VERSION_PREFIX + r'countries/', views.list_countries),

    # /api/1.0/population/
    url(API_VERSION_PREFIX + r'population/(?P<year>\d+)/(?P<country>.+)/(?P<age>\d+)/', views.list_population),
    url(API_VERSION_PREFIX + r'population/(?P<year>\d+)/(?P<country>.+)/', views.list_population),
    url(API_VERSION_PREFIX + r'population/(?P<country>.+)/(?P<age>\d+)/', views.list_population),

    # /api/1.0/wp-rank/
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'today/', views.wprank_today),
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'on/(?P<date>.+)/', views.wprank_by_date),
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'aged/(?P<age>.+)/', views.wprank_by_age),
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'ago/(?P<offset>.+)/', views.wprank_ago),
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'in/(?P<offset>.+)/', views.wprank_in),
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'ranked/(?P<rank>.+)/', views.wprank_by_rank),

    # /api/1.0/life-expectancy/
    url(API_VERSION_PREFIX + r'life-expectancy/remaining/(?P<sex>.+)/(?P<country>.+)/(?P<date>.+)/(?P<age>.+)/', views.life_expectancy_remaining),
    url(API_VERSION_PREFIX + r'life-expectancy/total/(?P<sex>.+)/(?P<country>.+)/(?P<dob>.+)', views.life_expectancy_total),

    # /api/docs/ (Swagger documentation)
    url(r'^docs/', include('rest_framework_swagger.urls')),
]
