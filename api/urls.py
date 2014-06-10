from django.conf.urls import patterns, include, url
from django.conf import settings
from api import views



API_VERSION_PREFIX = r'1.0/'
WP_RANK_PREFIX = r'wp-rank/'
PERSON_PATH = r'(?P<dob>.+)/(?P<sex>.+)/(?P<country>.+)/'


urlpatterns = [
    # /api/1.0/countries/
    url(API_VERSION_PREFIX + r'countries/', views.country_list),

    # /api/1.0/population/
    url(API_VERSION_PREFIX + r'population/(?P<year>\d+)/(?P<country>.+)/(?P<age>\d+)/', views.population_data),
    url(API_VERSION_PREFIX + r'population/(?P<year>\d+)/(?P<country>.+)/', views.population_data),
    url(API_VERSION_PREFIX + r'population/(?P<country>.+)/(?P<age>\d+)/', views.population_data),

    # /api/1.0/wp-rank/
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'today/', views.world_population_rank_today),
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'on/(?P<date>.+)/', views.world_population_rank_by_date),
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'aged/(?P<age>.+)/', views.world_population_rank_by_age),
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'ago/(?P<offset>.+)/', views.world_population_rank_in_past),
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'in/(?P<offset>.+)/', views.world_population_rank_in_future),
    url(API_VERSION_PREFIX + r'wp-rank/' + PERSON_PATH + r'ranked/(?P<rank>.+)/', views.date_by_world_population_rank),

    # /api/1.0/life-expectancy/
    url(API_VERSION_PREFIX + r'life-expectancy/remaining/(?P<sex>.+)/(?P<country>.+)/(?P<date>.+)/(?P<age>.+)/', views.remaining_life_expectancy),
    url(API_VERSION_PREFIX + r'life-expectancy/total/(?P<sex>.+)/(?P<country>.+)/(?P<dob>.+)', views.total_life_expectancy),

    # /api/docs/ (Swagger documentation)
    url(r'^docs/', include('rest_framework_swagger.urls')),
]
