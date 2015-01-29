from django.conf.urls import url
from api import views


WP_RANK_PREFIX = r'wp-rank/'
PERSON_PATH = r'(?P<dob>[^/]+)/(?P<sex>[^/]+)/(?P<country>[^/]+)/'


urlpatterns = [
    # /api/1.0/countries/
    url(r'countries/', views.list_countries),

    # /api/1.0/population/
    url(r'population/(?P<year>[^/]+)/(?P<country>[^/]+)/(?P<age>[^/]+)/', views.retrieve_population_table),
    url(r'population/(?P<year>\d+)/(?P<country>[^/]+)/', views.retrieve_population_table),
    url(r'population/(?P<country>[^/]+)/(?P<age>\d+)/', views.retrieve_population_table),
    url(r'population/(?P<country>[^/]+)/today-and-tomorrow/', views.retrieve_total_population_now),
    url(r'population/(?P<country>[^/]+)/(?P<refdate>[^/]+)/', views.retrieve_total_population),
    url(r'population/(?P<continent>[^/]+)/continent/(?P<refdate>[^/]+)/', views.retrieve_total_population_continent),

    # /api/1.0/wp-rank/
    url(r'wp-rank/' + PERSON_PATH + r'today/', views.world_population_rank_today),
    url(r'wp-rank/' + PERSON_PATH + r'on/(?P<date>[^/]+)/', views.world_population_rank_by_date),
    url(r'wp-rank/' + PERSON_PATH + r'aged/(?P<age>[^/]+)/', views.world_population_rank_by_age),
    url(r'wp-rank/' + PERSON_PATH + r'ago/(?P<offset>[^/]+)/', views.world_population_rank_in_past),
    url(r'wp-rank/' + PERSON_PATH + r'in/(?P<offset>[^/]+)/', views.world_population_rank_in_future),
    url(r'wp-rank/' + PERSON_PATH + r'ranked/(?P<rank>[^/]+)/', views.date_by_world_population_rank),

    # /api/1.0/life-expectancy/
    url(r'life-expectancy/remaining/(?P<sex>[^/]+)/(?P<country>[^/]+)/(?P<date>[^/]+)/(?P<age>[^/]+)/', views.calculate_remaining_life_expectancy),
    url(r'life-expectancy/total/(?P<sex>[^/]+)/(?P<country>[^/]+)/(?P<dob>[^/]+)/', views.total_life_expectancy),

    # /api/1.0/mortality-distribution/
    url(r'mortality-distribution/(?P<country>[^/]+)/(?P<sex>[^/]+)/(?P<age>[^/]+)/today/', views.calculate_mortality_distribution),
]
