''' 
R to python: yourRank.r

'''
import os
from datetime import datetime, timedelta
from django.conf import settings

import numpy as np
import pandas as pd
from scipy.interpolate import InterpolatedUnivariateSpline



inputData = os.path.join(settings.BASE_DIR, 'data', 'WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.csv')

# -- Read in Data --- #
# UN population by age in single years and sex annually during 1950-2100
print 'Sourcing CSV...'
data = pd.read_csv(inputData)
print 'done.'
#pickle.dump(data, open('pop_data.pickle', 'wb'))
#	print data.head()

print 'Preprocessing...'
# store columns to objects:
Location = data.Location
#Time = data.Time
Age = data.Age
#PopMale = data.PopMale
#PopFemale = data.PopFemale
#PopTotal = data.PopTotal

# -- Change the value of Australia -- #
Location = Location.replace("Australia/New Zealand", "Australia and New Zealand")

# -- Get list of countries -- #
countries = pd.unique(Location)

''' --- Date Range Wrangling --- '''
# -- Date field manipulation: Get date Range, note: Annual data are for the 1st of July -- #
date_format = '%Y/%m/%d' # define the time format 	#dts = Time.map(lambda x: str(x) + "/07/01")
# Get the unique years (between 1950 - 2100)
dts = pd.unique(data.Time)
#	print dts

# Define function to add July 1st
def addJuly(d) :
    return datetime.strptime((str(d) + "/07/01"), date_format)
addJuly = np.vectorize(addJuly) # vectorize the function to iterate over numpy ndarray
dts = addJuly(dts) # 1st result: " datetime.datetime(1950, 7, 1, 0, 0) "
#	print dts

# Define function to get Date as numeric
refDate = datetime.strptime('1970/01/01', date_format)
def numDate(d):
    return (d - refDate).days # get back "days" by calling .days object
numDate = np.vectorize(numDate) # vectorize the function to iterate over numpy ndarray
date2 = numDate(dts) # 1st result: -7124
#	print date2

# Define the FULL range from 1st of Jan 1950 to 31st dec 2100 store in array
date2Min = np.min(date2)
date2Max = np.max(date2)
dateLowest = date2Min - ((date2Min) - numDate(datetime.strptime('1950/01/01', date_format)))
dateHighest = (numDate(datetime.strptime('2100/12/31', date_format)) - date2Max) + date2Max
#xout = []
xout = [dateLowest, dateHighest]
#	print xout

# AGE in days refering to the annual data - we assume that the average age of one years old is 1 years and 183 days
age3 = range(0,100)
age3 = [ x*365+183 for x in age3]

# Range of days (age)
ageout = range(0, 36501)

''' --- function doitall() start --- '''
def doitall(region, gender):
    """
    Function that extrapolates the 1st July data to each calender day

    :param region: valid values: anything from 'countries'
    :param gender: valid values: PopFemale, PopMale, PopTotal
    :return: an extrapolation table for the given region/gender tuple
    """
    pop1 = data[Location == region]
    pop1 = pop1[['Time', 'Age', gender]]
    # pop1 = data[['Time', 'Age', SEX]].query('Location' == CNTRY)
    #print pop1

    ''' --- Date interpolation function --- '''
    def dateInterp(iage):
        popi = pop1[Age == iage]
        #popi = pop1[Age == 21] #select particular age COMMENT OUT
        popi = np.asarray(popi[gender])
        #print popi

        # spline interpolation function from Scipy Package
        days= range(xout[0], xout[1]+1)
        iuspl = InterpolatedUnivariateSpline(date2, popi)
        iuspl_pred = iuspl(days)
        return iuspl_pred
        #print iuspl_pred[1:10]
        #print iuspl_pred.size

        # TEST: spline interpolation function from Scipy Package
        # days= range(xout[0], xout[1])
        # ispl = splrep(date2, popi )
        # print ispl
    ''' --- function end --- '''
    # store the results of the date interpolation
    result1 =[]
    for i in range(0,100):
        result1.append(np.array(dateInterp(i)))
    # List to pandas dataframe | dataframe.T transposes data
    result1 = pd.DataFrame(result1).T # from 55151col x 100row --> 55151row x 100col

    # Change column names by appending "age_"
    oldHeaders = result1.columns
    newHeaders = []
    for i in oldHeaders:
        newHeaders.append("age" + "_" + str(i))
    result1.columns = newHeaders
    #print result1.head # results: "age_0, age_1, ..."

    # Convert the numerical days to date string
    days= range(xout[0], xout[1]+1) # the full date range in days from 1970/01/01 - 2100/12/31
    def toDate(d):
        return (refDate + timedelta(days=d)).strftime('%Y-%m-%d')
    toDate = np.vectorize(toDate) # vectorize the function to iterate over numpy ndarray
    fullDateRange = toDate(days) # 1st result: 1950-01-01

    # Add the fullDateRange to the result1
    result1['date1'] = fullDateRange
    #print result1['date1']

    # End the doitall function
    return result1

# generate extrapolation table
pop2 = doitall('WORLD', 'PopTotal')

# we could cache the result in a CSV here:
# pop2.to_csv(CNTRY+iSEX+".csv")

print 'done.'

''' --- function that interpolates age in days -- '''
# create function pyTime to convert date1 field
#pyTime =  np.vectorize(lambda d: datetime.strptime(d, '%Y-%m-%d') )
def dayInterpA(iDate):
    # age 0 to 99
    popi = pop2[pop2.date1 == iDate]

    # Remove the columns for age 100 and the date1
    rmCols = [col for col in popi.columns if col not in ['date1', 'age_100']]
    popi = popi[rmCols]

    # store the popi results into an array for the interpolation
    #popi = (np.asarray(popi)).tolist()
    popi = popi.values
    popi = [vals for i in popi for vals in i]
    popi = np.asarray(popi)

    # Interpolate the age in Days
    iuspl2 = InterpolatedUnivariateSpline(age3, popi/365)
    iuspl2_pred = iuspl2(ageout)

    # the output
    col1 = pd.DataFrame(ageout, columns=['AGE'])
    col2 = pd.DataFrame(iuspl2_pred, columns = ['POP'])
    #print col1, col2
    merged = col1.join(col2)
    #print merged
    #return pd.DataFrame(ageout, iuspl2_pred, columns=['AGE', 'POP'])
    return merged

# my rank by date: What will be my rank on particular day
def worldPopulationRankByDate(dob, date):
    iAge = numDate(date) - numDate(dob)
    X = dayInterpA(date.strftime('%Y-%m-%d'))

    # store age and pop in array
    ageArray = np.asarray(X.AGE)
    popArray = np.asarray(X.POP)

    # calc cumulative sum of the population
    cumSum =  np.cumsum(popArray)

    # take the mean of the cumulative sum of the iAge year and preceeding
    rank = np.mean(np.extract((ageArray >= iAge -1) & (ageArray <= iAge), cumSum))
    return long(rank*1000)
