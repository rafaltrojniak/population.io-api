import datetime
from dateutil.relativedelta import relativedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.datastore import dataStore
from api.decorators import expect_date, expect_offset, expect_int, cache_until_utc_eod, cache_unlimited
from api.utils import offset_to_str
from api.algorithms import worldPopulationRankByDate, dateByWorldPopulationRank, lifeExpectancyRemaining, lifeExpectancyTotal, populationCount, \
    totalPopulation, calculateMortalityDistribution


@api_view(['GET'])
@cache_unlimited()
def list_countries(request):
    """ Return a list of all countries in the statistical dataset. These are also the valid input values to the various 'country' parameters across the remaining API.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    return Response({'countries': dataStore.countries})


@api_view(['GET'])
@cache_until_utc_eod()
@expect_date('dob')
def world_population_rank_today(request, dob, sex, country):
    """ Calculates the world population rank of a person with the given date of birth, sex and country of origin as of today.<p>The world population rank is defined as the position of someone's birthday among the group of living people of the same sex and country of origin, ordered by date of birth increasing. The first person born is assigned rank #1.<p>Today's date is always based on the current time in the timezone UTC.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    today = datetime.datetime.utcnow().date()
    rank = worldPopulationRankByDate(sex, country, dob, today)
    return Response({"rank": rank, 'dob': dob, 'sex': sex, 'country': country})


@api_view(['GET'])
@cache_unlimited()
@expect_date('dob')
@expect_date('date')
def world_population_rank_by_date(request, dob, sex, country, date):
    """ Calculates the world population rank of a person with the given date of birth, sex and country of origin on a certain date.<p>The world population rank is defined as the position of someone's birthday among the group of living people of the same sex and country of origin, ordered by date of birth increasing. The first person born is assigned rank #1.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    rank = worldPopulationRankByDate(sex, country, dob, date)
    return Response({"rank": rank, 'dob': dob, 'sex': sex, 'country': country, 'date': date})


@api_view(['GET'])
@cache_unlimited()
@expect_date('dob')
@expect_offset('age')
def world_population_rank_by_age(request, dob, sex, country, age):
    """ Calculates the world population rank of a person with the given date of birth, sex and country of origin on a certain date as expressed by the person's age.<p>The world population rank is defined as the position of someone's birthday among the group of living people of the same sex and country of origin, ordered by date of birth increasing. The first person born is assigned rank #1.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    rank = worldPopulationRankByDate(sex, country, dob, dob + age)
    return Response({"rank": rank, 'dob': dob, 'sex': sex, 'country': country, 'age': offset_to_str(age)})


@api_view(['GET'])
@cache_until_utc_eod()
@expect_date('dob')
@expect_offset('offset')
def world_population_rank_in_past(request, dob, sex, country, offset):
    """ Calculates the world population rank of a person with the given date of birth, sex and country of origin on a certain date as expressed by an offset towards the past from today.<p>The world population rank is defined as the position of someone's birthday among the group of living people of the same sex and country of origin, ordered by date of birth increasing. The first person born is assigned rank #1.<p>Today's date is always based on the current time in the timezone UTC.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    today = datetime.datetime.utcnow().date()
    rank = worldPopulationRankByDate(sex, country, dob, today - offset)
    return Response({"rank": rank, 'dob': dob, 'sex': sex, 'country': country, 'offset': offset_to_str(offset)})


@api_view(['GET'])
@cache_until_utc_eod()
@expect_date('dob')
@expect_offset('offset')
def world_population_rank_in_future(request, dob, sex, country, offset):
    """ Calculates the world population rank of a person with the given date of birth, sex and country of origin on a certain date as expressed by an offset towards the future from today.<p>The world population rank is defined as the position of someone's birthday among the group of living people of the same sex and country of origin, ordered by date of birth increasing. The first person born is assigned rank #1.<p>Today's date is always based on the current time in the timezone UTC.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    today = datetime.datetime.utcnow().date()
    rank = worldPopulationRankByDate(sex, country, dob, today + offset)
    return Response({"rank": rank, 'dob': dob, 'sex': sex, 'country': country, 'offset': offset_to_str(offset)})


@api_view(['GET'])
@cache_unlimited()
@expect_date('dob')
@expect_int('rank')
def date_by_world_population_rank(request, dob, sex, country, rank):
    """ Calculates the day on which a person with the given date of birth, sex and country of origin has reached (or will reach) a certain world population rank.<p>The world population rank is defined as the position of someone's birthday among the group of living people of the same sex and country of origin, ordered by date of birth increasing. The first person born is assigned rank #1.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    calcdate = dateByWorldPopulationRank(sex, country, dob, rank)
    return Response({'dob': dob, 'sex': sex, 'country': country, 'rank': rank, 'date_on_rank': calcdate})


@api_view(['GET'])
@cache_unlimited()
@expect_date('date')
@expect_offset('age')
def calculate_remaining_life_expectancy(request, sex, country, date, age):
    """ Calculate remaining life expectancy of a person with given sex, country, and age at a given point in time.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    remaining_life_expectancy = lifeExpectancyRemaining(sex, country, date, age)
    return Response({'date': date, 'sex': sex, 'country': country, 'age': offset_to_str(age), 'remaining_life_expectancy': remaining_life_expectancy})


@api_view(['GET'])
@cache_unlimited()
@expect_date('dob')
def total_life_expectancy(request, sex, country, dob):
    """ Calculate total life expectancy of a person with given sex, country, and date of birth.<p>Note that this function is implemented based on the remaining life expectancy by picking a reference date based on an age of 35 years. It is therefore of limited accuracy.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    total_life_expectancy = lifeExpectancyTotal(sex, country, dob)
    return Response({'dob': dob, 'sex': sex, 'country': country, 'total_life_expectancy': total_life_expectancy})


@api_view(['GET'])
@cache_unlimited()
@expect_int('age', optional=True)
@expect_int('year', optional=True)
def retrieve_population_table(request, country, age=None, year=None):
    """ Retrieve population table for age group / year / country.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    result = populationCount(country, age, year)
    # FIXME: the API currently returns a flat JS array here, which is invalid JSON. The commented out line would fix this, but is currently deactivated as not to break the frontend!
    return Response(result)
    #return Response({"tables": result})


@api_view(['GET'])
@cache_until_utc_eod()   # may only be cached until the day ends, as it is dependent on the current system date
def retrieve_total_population_now(request, country):
    """ Retrieve total population count for country today and tomorrow.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    today = datetime.datetime.utcnow().date()
    tomorrow = today + relativedelta(days=1)
    population_today = {'date': today, 'population': totalPopulation(country, today)}
    population_tomorrow = {'date': tomorrow, 'population': totalPopulation(country, tomorrow)}
    return Response({'total_population': [population_today, population_tomorrow]})


@api_view(['GET'])
@cache_unlimited()
@expect_date('refdate')
def retrieve_total_population(request, country, refdate):
    """ Retrieve total population count for country on given date.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    result = {'date': refdate, 'population': totalPopulation(country, refdate)}
    return Response({'total_population': result})


@api_view(['GET'])
@cache_unlimited()
@expect_offset('age')
def calculate_mortality_distribution(request, country, sex, age):
    """ Retrieve mortality distribution for given country / sex / age.<p>
        Please see <a href="/">the full API browser</a> for more information.
    """
    plain_distribution = calculateMortalityDistribution(country, sex, age)
    mortality_distribution = [{'age': val[0], 'mortality_percent': val[1]} for val in plain_distribution]
    return Response({'mortality_distribution': mortality_distribution})
