''' 
R to python: yourRank.r

'''
import os
from datetime import datetime, timedelta
from django.conf import settings

import numpy as np
import pandas as pd
from scipy.interpolate import InterpolatedUnivariateSpline



POSIX_EPOCH = datetime(1970, 1, 1)
def inPosixDays(date):
    """
    Transforms a datetime object into 'posix days', here defined as the days since the posix epoch, Jan 1, 1970.

    :param date: a datetime object
    :return: the corresponding 'posix days' to the given datetime object
    """
    return (date - POSIX_EPOCH).days



class WorldPopulationRankCalculator(object):

    # AGE in days refering to the annual data - we assume that the average age of one years old is 1 years and 183 days
    AGE3 = [x*365+183 for x in range(0,100)]

    # Range of days (age)
    AGEOUT = range(0, 36501)

    def __init__(self):
        # -- Read in Data --- #
        print 'Sourcing CSV...'
        # UN population by age in single years and sex annually during 1950-2100
        inputData = os.path.join(settings.BASE_DIR, 'data', 'WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.csv')
        self.data = pd.read_csv(inputData)
        print 'done.'

        # -- Change the value of Australia -- #
        self.data.Location = self.data.Location.replace("Australia/New Zealand", "Australia and New Zealand")

        # -- Get list of countries -- #
        self.countries = pd.unique(self.data.Location)

    ''' --- function doitall() start --- '''
    def doitall(self, region, gender):
        """
        Function that extrapolates the 1st July data to each calender day

        :param region: valid values: anything from 'countries'
        :param gender: valid values: PopFemale, PopMale, PopTotal
        :return: an extrapolation table for the given region/gender tuple
        """
        pop1 = self.data[self.data.Location == region]
        pop1 = pop1[['Time', 'Age', gender]]
        # pop1 = data[['Time', 'Age', SEX]].query('Location' == CNTRY)
        #print pop1

        july1from1950to2100 = [inPosixDays(datetime(y, 7, 1)) for y in xrange(1950, 2100+1)]

        dateRange1970to2100inPosixDays = range(inPosixDays(datetime(1950,1,1)), inPosixDays(datetime(2100,12,31))+1)

        ''' --- Date interpolation function --- '''
        def dateInterp(iage):
            popi = pop1[self.data.Age == iage]
            #popi = pop1[Age == 21] #select particular age COMMENT OUT
            popi = np.asarray(popi[gender])

            # spline interpolation function from Scipy Package
            iuspl = InterpolatedUnivariateSpline(july1from1950to2100, popi)
            iuspl_pred = iuspl(dateRange1970to2100inPosixDays)
            return iuspl_pred
        ''' --- function end --- '''

        # store the results of the date interpolation
        result1 = []
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
        def toDate(d):
            return (datetime(1970, 1, 1) + timedelta(days=d)).strftime('%Y-%m-%d')
        toDate = np.vectorize(toDate) # vectorize the function to iterate over numpy ndarray
        fullDateRange = toDate(dateRange1970to2100inPosixDays) # 1st result: 1950-01-01

        # Add the fullDateRange to the result1
        result1['date1'] = fullDateRange

        # End the doitall function
        global pop2
        pop2 = result1
        return result1

    ''' --- function that interpolates age in days -- '''
    # create function pyTime to convert date1 field
    #pyTime =  np.vectorize(lambda d: datetime.strptime(d, '%Y-%m-%d') )
    def dayInterpA(self, iDate):
        global pop2
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
        iuspl2 = InterpolatedUnivariateSpline(WorldPopulationRankCalculator.AGE3, popi/365)
        iuspl2_pred = iuspl2(WorldPopulationRankCalculator.AGEOUT)

        # the output
        col1 = pd.DataFrame(WorldPopulationRankCalculator.AGEOUT, columns=['AGE'])
        col2 = pd.DataFrame(iuspl2_pred, columns = ['POP'])
        #print col1, col2
        merged = col1.join(col2)
        #print merged
        #return pd.DataFrame(ageout, iuspl2_pred, columns=['AGE', 'POP'])
        return merged

    def worldPopulationRankByDate(self, dob, date):
        """
        my rank by date: What will be my rank on particular day

        :param dob:
        :param date:
        :return:
        """
        iAge = inPosixDays(date) - inPosixDays(dob)
        X = self.dayInterpA(date.strftime('%Y-%m-%d'))

        # store age and pop in array
        ageArray = np.asarray(X.AGE)
        popArray = np.asarray(X.POP)

        # calc cumulative sum of the population
        cumSum =  np.cumsum(popArray)

        # take the mean of the cumulative sum of the iAge year and preceeding
        rank = np.mean(np.extract((ageArray >= iAge -1) & (ageArray <= iAge), cumSum))
        return long(rank*1000)



#print 'Preprocessing...'
# generate extrapolation table
#calc = WorldPopulationRankCalculator()
#pop2 = calc.doitall('WORLD', 'PopTotal')

# we could cache the result in a CSV here:
# pop2.to_csv(CNTRY+iSEX+".csv")

#print 'done.'
