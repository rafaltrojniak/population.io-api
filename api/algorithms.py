''' 
R to python: yourRank.r
'''
import math
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
from scipy.interpolate import InterpolatedUnivariateSpline

from api.exceptions import *
from api.datastore import dataStore

from api.utils import relativedelta_to_decimal_years



# AGE in days refering to the annual data - we assume that the average age of one years old is 1 years and 183 days
AGE3 = [x*365+183 for x in range(0,100)]

# Range of days (age)
AGEOUT = range(0, 36501)

SEXES = {'male': 'PopMale', 'female': 'PopFemale', 'unisex': 'PopTotal',}
SEXES_LIFE_EXPECTANCY = {'male': 1, 'female': 2,}

POSIX_EPOCH = date(1970, 1, 1)
def inPosixDays(date):
    """
    Transforms a datetime object into 'posix days', here defined as the days since the posix epoch, Jan 1, 1970.

    :param date: a datetime object
    :return: the corresponding 'posix days' to the given datetime object
    """
    return (date - POSIX_EPOCH).days

def generateExtrapolationTable(sex, region):
    """
    Function that extrapolates the 1st July data to each calender day

    :param region: valid values: anything from 'regions'
    :param sex: valid values: female, male, unisex
    :return: an extrapolation table for the given region/sex tuple
    """
    pop1 = dataStore.data[dataStore.data.Location == region]
    pop1 = pop1[['Time', 'Age', SEXES[sex]]]
    # pop1 = data[['Time', 'Age', SEX]].query('Location' == CNTRY)
    #print pop1

    july1from1950to2100 = [inPosixDays(date(y, 7, 1)) for y in xrange(1950, 2100+1)]

    dateRange1970to2100inPosixDays = range(inPosixDays(date(1950,1,1)), inPosixDays(date(2100,12,31))+1)

    ''' --- Date interpolation function --- '''
    def dateInterp(iage):
        popi = pop1[dataStore.data.Age == iage]
        #popi = pop1[Age == 21] #select particular age COMMENT OUT
        popi = np.asarray(popi[SEXES[sex]])

        # spline interpolation function from Scipy Package
        iuspl = InterpolatedUnivariateSpline(july1from1950to2100, popi)
        iuspl_pred = iuspl(dateRange1970to2100inPosixDays)
        return iuspl_pred
    ''' --- function end --- '''

    # store the results of the date interpolation
    table = []
    for i in range(0,100):
        table.append(np.array(dateInterp(i)))
    # List to pandas dataframe | dataframe.T transposes data
    table = pd.DataFrame(table).T # from 55151col x 100row --> 55151row x 100col

    # Change column names by appending "age_"
    oldHeaders = table.columns
    newHeaders = []
    for i in oldHeaders:
        newHeaders.append("age" + "_" + str(i))
    table.columns = newHeaders
    #print result1.head # results: "age_0, age_1, ..."

    # Convert the numerical days to date string
    def toDate(d):
        return (date(1970, 1, 1) + timedelta(days=d)).strftime('%Y-%m-%d')
    toDate = np.vectorize(toDate) # vectorize the function to iterate over numpy ndarray
    fullDateRange = toDate(dateRange1970to2100inPosixDays) # 1st result: 1950-01-01

    # Add the fullDateRange to the result1
    table['date1'] = fullDateRange

    return table
dataStore.registerTableBuilder(generateExtrapolationTable)   # TODO: not super nice architecture, but avoids the cyclic dependency for now

def dayInterpA(table, date):
    """
    function that interpolates age in days

    :param table: the extrapolation table to use
    :param date: the date
    :return:
    """
    iDate = date.strftime('%Y-%m-%d')
    # age 0 to 99
    popi = table[table.date1 == iDate]

    # Remove the columns for age 100 and the date1
    rmCols = [col for col in popi.columns if col not in ['date1', 'age_100']]
    popi = popi[rmCols]

    # store the popi results into an array for the interpolation
    #popi = (np.asarray(popi)).tolist()
    popi = popi.values
    popi = [vals for i in popi for vals in i]
    popi = np.asarray(popi)

    # Interpolate the age in Days
    iuspl2 = InterpolatedUnivariateSpline(AGE3, popi/365)
    iuspl2_pred = iuspl2(AGEOUT)

    # the output
    col1 = pd.DataFrame(AGEOUT, columns=['AGE'])
    col2 = pd.DataFrame(iuspl2_pred, columns = ['POP'])
    #print col1, col2
    merged = col1.join(col2)
    #print merged
    #return pd.DataFrame(ageout, iuspl2_pred, columns=['AGE', 'POP'])
    return merged

def _calculateRankByDate(table, dob, date):
    # do the interpolation
    iAge = inPosixDays(date) - inPosixDays(dob)   # FIXME: isn't this just (date - dob).days?
    X = dayInterpA(table, date)

    # store age and pop in array
    ageArray = np.asarray(X.AGE)
    popArray = np.asarray(X.POP)

    # calc cumulative sum of the population
    cumSum =  np.cumsum(popArray)

    # take the mean of the cumulative sum of the iAge year and preceeding
    rank = np.mean(np.extract((ageArray >= iAge -1) & (ageArray <= iAge), cumSum))
    if not rank > 0:
        raise RuntimeError('Rank calculation failed due to internal error')   # we should never get here, if we do that means the parameter checks at the beginning are incomplete
    return rank

def worldPopulationRankByDate(sex, region, dob, refdate):
    """
    my rank by date: What will be my rank on particular day

    :param sex:
    :param region:
    :param dob:
    :param refdate:
    :return:
    """
    # check that all arguments have the right type (even though it's not very pythonic)
    if not isinstance(sex, basestring) or not isinstance(region, basestring) or not isinstance(dob, date) or not isinstance(refdate, date):
        raise TypeError('One or more arguments did not match the expected parameter type')

    # confirm that sex and region contain valid values
    if sex not in SEXES:
        raise InvalidSexError(sex)
    if region not in dataStore.countries:
        raise InvalidCountryError(region)

    # check the various date requirements
    today = datetime.utcnow().date()
    if dob < date(1920, 1, 1) or dob > today:
        raise BirthdateOutOfRangeError(dob, 'between 1920-01-01 and today')
    if refdate < date(1950, 1, 1) or refdate < dob:
        raise CalculationDateOutOfRangeError(refdate, 'past 1950-01-01 and past the birthdate')
    if (refdate - dob).days > 36500:
        raise CalculationTooWideError(refdate)

    # retrieve or build the extrapolation table for this (sex, region) tuple
    table = dataStore[sex, region]

    # do the calculations
    rank = _calculateRankByDate(table, dob, refdate)
    return long(rank*1000)

def dateByWorldPopulationRank(sex, region, dob, rank):
    """
    finding the date for specific rank

    :param birth:
    :param wRank:
    :return:
    """
    # check that all arguments have the right type (even though it's not very pythonic)
    if not isinstance(sex, basestring) or not isinstance(region, basestring) or not isinstance(dob, date):
        raise TypeError('One or more arguments did not match the expected parameter type')

    # confirm that sex and region contain valid values
    if sex not in SEXES:
        raise InvalidSexError(sex)
    if region not in dataStore.countries:
        raise InvalidCountryError(region)

    # check the various date requirements
    if dob < date(1920, 1, 1) or dob > date(2079, 12, 31):   # the end date has been chosen arbitrarily and is probably wrong
        raise BirthdateOutOfRangeError(dob, 'between 1920-01-01 and 2079-12-31')

    # internally, the algorithm works with k-ranks
    rank = rank / 1000.0

    # prefetch the extrapolation table
    table = dataStore[sex, region]

    # The number of years from input birth to '2100/01/01'
    length_time = relativedelta(date(2100, 1, 1), dob).years

    # Make sure that difference between DOB and final Date > 100
    if length_time < 100:
        l_max = np.round(length_time)
    else:
        l_max = 100

    xx = []
    for jj in range(1, (len(range(10, l_max+10, 10))+1)):
        try:
            xx.append(_calculateRankByDate(table, dob, dob + relativedelta(days = jj*3650)))
        except Exception:
            # Breaks the function if either the birthdate is too late for some rank or the rank is too high for some birthdate
            raise DataOutOfRangeError(detail='The input data is out of range: the birthdate is too late for the rank or the rank is too high for the birthdate')

    # check the array for NaN?
    xx = np.array(xx) # convert xx from list to array
    #nanIndex = np.where(np.isnan(xx)) # return array of index positions for NANs

    ''' NEED TO BREAK THE FUNCTION IF CC IS TRUE - NOT YET IMPLEMENTED '''
    # check to see if all of the Ranks are less than the wRank
    if np.all(xx < rank):
        raise DataOutOfRangeError(detail='The input data is out of range: the person is too young')

    #print xx
    # now find the interval containing wRank
    #print rank
    #print np.amin(np.where((xx < rank) == False))
    Upper_bound = (np.amin(np.where((xx < rank) == False))+1)*10 # +1 because of zero index
    Lower_bound = Upper_bound-10

    if Lower_bound < 2:
        # I don't know what this error means, but if Lower_bound is < 2, then range_2 will start with a value < 0
        # which means _calculateRankByDate() will be called with a negative age, and that will fail
        raise DataOutOfRangeError()

    #print Upper_bound, Lower_bound

    # Define new range
    range_2 = np.arange(Lower_bound-2, Upper_bound+1) # +1 due to zero index

    # locate the interval
    xx_ = np.zeros((len(range_2),2))

    # given that interval, do a yearly interpolation
    #print range_2
    for kk in range_2:
        #print kk
        xx_[(kk - np.amin(range_2)),0] = _calculateRankByDate(table, dob, dob + relativedelta(years=kk))
        xx_[(kk - np.amin(range_2)),1] = kk*365

    # Search again for the yearly interval containing wRank
    Upper_bound = xx_[np.amin(np.where((xx_[:,0] < rank) == False)),1]
    Lower_bound = xx_[np.amax(np.where((xx_[:,0] < rank) == True)),1]

    range_3 = np.arange(Lower_bound, Upper_bound+1)
    #print (range_3)

    #xx_ = np.zeros((len(range_3),2))

    # From this point on, this stuff is within a year (daily), due to the fact that the evolution of the rank is linear
    # we do linear interpolation to get the exact day faster
    end_point = range_3[len(range_3)-1]
    first_point = range_3[0]
    # print end_point, first_point

    # Get the rank for the first and last days in range_3
    rank_end = _calculateRankByDate(table, dob, dob + relativedelta(days=end_point))
    rank_first = _calculateRankByDate(table, dob, dob + relativedelta(days=first_point))

    # This gives us the age when we reach wRank and the exact date
    final_age = np.interp(rank, [rank_first, rank_end], [Lower_bound, Upper_bound])
    final_date = dob + relativedelta(days=final_age)
    #print final_age, final_date

    ''' CHECK THESE INTERPOLATION VALUES '''
    #now we also want to plot our life-path, so we do spline interpolation for the stuff we calculated in the first step
    # (i.e. the ranks over decades) and interpolate using bSplines.
    #xx_interp = InterpolatedUnivariateSpline((np.arange(10, l_max+1, 10)*365),xx)
    # print xx_interp
    #x_interp = xx_interp((np.arange(1,36501,365)))
    # print x_interp

    # find the rank nearest to wRank
    #find_r = np.amin(np.where(abs(x_interp - rank)))
    # print find_r

    # The value this function returns
    #exactAge = round(final_age/365, 1)
    #age = math.floor(final_age/365)
    #DATE = final_date

    #pd.DataFrame({'exactAge': pd.Series([exactAge], index = ['1']), 'age': pd.Series([age],index = ['1']), 'DATE': pd.Series([DATE], index = ['1'])})
    return final_date

def lifeExpectancyRemaining(sex, region, refdate, age):
    # check that all arguments have the right type (even though it's not very pythonic)
    if not isinstance(sex, basestring) or not isinstance(region, basestring) or not isinstance(refdate, date) or not isinstance(age, relativedelta):
        raise TypeError('One or more arguments did not match the expected parameter type')

    # confirm that sex and region contain valid values
    if sex not in SEXES_LIFE_EXPECTANCY:
        raise InvalidSexError(sex)
    if region not in dataStore.countries:
        raise InvalidCountryError(region)

    # check the various date requirements
    if refdate < date(1955, 1, 1) or refdate >= date(2095, 1, 1):
        raise CalculationDateOutOfRangeError(refdate, 'from 1955-01-01 to 2094-12-31')
    age_float = relativedelta_to_decimal_years(age)
    if age_float > 100:
        raise AgeOutOfRangeError(age)
    if refdate - age > date(2015, 6, 30):
        raise EffectiveBirthdateOutOfRangeError(invalidValue=(refdate-age))

    # find beginning of 5 yearly period for the le_date
    le_yr = refdate.year   #(le_date.loc['1'])[0:4]
    lowest_year = math.floor(int(le_yr)/5)*5

    # extract a row corresponding to the time-period
    life_exp_prd_5below = dataStore.life_expectancy_ages[(dataStore.life_expectancy_ages.region == region) & (dataStore.life_expectancy_ages.sex == SEXES_LIFE_EXPECTANCY[sex]) & (dataStore.life_expectancy_ages.Begin_prd == lowest_year-5)]
    life_exp_prd_ext = dataStore.life_expectancy_ages[(dataStore.life_expectancy_ages.region == region) & (dataStore.life_expectancy_ages.sex == SEXES_LIFE_EXPECTANCY[sex]) & (dataStore.life_expectancy_ages.Begin_prd == lowest_year)]
    life_exp_prd_5above = dataStore.life_expectancy_ages[(dataStore.life_expectancy_ages.region == region) & (dataStore.life_expectancy_ages.sex == SEXES_LIFE_EXPECTANCY[sex]) & (dataStore.life_expectancy_ages.Begin_prd == lowest_year+5)]

    # life_exp_prd
    life_exp_prd = pd.concat([life_exp_prd_5below, life_exp_prd_ext, life_exp_prd_5above])
    life_exp_prd = life_exp_prd.ix[:,4:len(life_exp_prd.columns)]

    # Place holder for Agenames and values for three consecutive periods of interest
    life_exp_ = np.zeros((len(life_exp_prd.columns), 4))

    # Age group starting at and less than the next value: 0, 1, 5, 10
    life_exp_[:,0] = np.insert((np.arange(5, 130, 5)), 0, [0,1])

    # transpose the dataframe - prep for assinging life expectancy vals
    life_exp_prd = life_exp_prd.T

    # Assigning life expectancy values
    life_exp_[:,1] = life_exp_prd[life_exp_prd.columns[0]].values
    life_exp_[:,2] = life_exp_prd[life_exp_prd.columns[1]].values
    life_exp_[:,3] = life_exp_prd[life_exp_prd.columns[2]].values

    # interpolations
    xx_interp1 = InterpolatedUnivariateSpline(life_exp_[(np.amax(max(np.where(life_exp_[:,1] == 0)))):,0], life_exp_[(np.amax(max(np.where(life_exp_[:,1] == 0)))):,1])
    xx_interp2 = InterpolatedUnivariateSpline(life_exp_[(np.amax(max(np.where(life_exp_[:,2] == 0)))):,0], life_exp_[(np.amax(max(np.where(life_exp_[:,2] == 0)))):,2])
    xx_interp3 = InterpolatedUnivariateSpline(life_exp_[(np.amax(max(np.where(life_exp_[:,3] == 0)))):,0], life_exp_[(np.amax(max(np.where(life_exp_[:,3] == 0)))):,3])

    # predictions
    x_interp1 = xx_interp1(age_float)   #interpolated value for AGE in earlier 5 yearly period
    x_interp2 = xx_interp2(age_float)   #interpolated value for AGE in the 5 yearly period of interest
    x_interp3 = xx_interp3(age_float)   #interpolated value for AGE in 5 yearly period after

    # matrix of vals
    life_exp_yr = np.zeros((3,2))

    #The mid point of period 2010-2015 which is from 1st July 2010 to June 30 of 2015, therefore, the mid point is 1st Jan 2013
    #In the following we turn the year to the date and then to numeric. We will use these to interpolate between periods and then predict the le for exact date
    addDate = lambda d: inPosixDays(date(int(d)+3, 1, 1))

    life_exp_yr[:,0] = [addDate(lowest_year-5), addDate(lowest_year), addDate(lowest_year+5)]
    life_exp_yr[:,1] = [x_interp1, x_interp2, x_interp3]

    return life_exp_yr[0,1]
    #life_exp_yr[,1]<- as.numeric(as.Date(c(paste(lowest_yr-5+3,1,1,sep="/"),paste(lowest_yr+3,1,1,sep="/"),paste(lowest_yr+5+3,1,1,sep="/")),"%Y/%m/%d"))

def lifeExpectancyTotal(sex, region, dob):
    if not isinstance(dob, date):
        raise TypeError('One or more arguments did not match the expected parameter type')

    if dob < date(1920, 1, 1) or dob > date(2059, 12, 31):
        raise BirthdateOutOfRangeError(dob, 'between 1920-01-01 and 2059-12-31')

    age = relativedelta(years=35)   # set an arbitrary age that keeps our calculation in the boundaries of lifeExpectancyRemaining()
    age_float = relativedelta_to_decimal_years(age)
    refdate = dob + age
    return age_float + lifeExpectancyRemaining(sex, region, refdate, age)

def populationCount(country, age=None, year=None):
    # check that all arguments have the right type (even though it's not very pythonic)
    if not isinstance(country, basestring) or (age is not None and not isinstance(age, int)) or (year is not None and not isinstance(year, int)):
        raise TypeError('One or more arguments did not match the expected parameter type')

    # confirm that sex and region contain valid values
    if country not in dataStore.countries:
        raise InvalidCountryError(country)

    # check the various date requirements
    if age is None and year is None:   # note: age can be 0, so we have to check for None here, checking for truthyness is *not* sufficient!
        raise DataOutOfRangeError('Either an age or a year have to be specified')
    if age is not None and (age < 1 or age > 100):   # FIXME: actually, an age of 0 should be valid, but the lookup with Pandas doesn't work for some reason
        raise DataOutOfRangeError('The age %i can not be processed, because only ages between 1 and 100 years are supported' % age)
    if year is not None and (year < 1950 or year > 2100):
        raise DataOutOfRangeError('The year %i can not be processed, because only years between 1950 and 2100 are supported' % year)

    data = dataStore.data[dataStore.data['Location']==country]
    if age:
        data = data[dataStore.data['Age']==age]
    if year:
        data = data[dataStore.data['Time']==year]
    results = []
    for row in data.iterrows():
        series = row[1]
        results.append({'year': series['Time'], 'age': series['Age'], 'males': int(series['PopMale']*1000), 'females': int(series['PopFemale']*1000), 'total': int(series['PopTotal']*1000)})
    return results
