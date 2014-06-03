''' 
R to python: yourRank.r
'''
import os, time
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

    SEXES = ('PopMale', 'PopFemale', 'PopTotal',)

    #REGIONS = [x.decode('latin1').encode('ascii') for x in ('Afghanistan', 'Albania', 'Algeria', 'Angola', 'Antigua and Barbuda', 'Azerbaijan', 'Argentina', 'Australia', 'Austria', 'Bahamas', 'Bahrain', 'Bangladesh', 'Armenia', 'Barbados', 'Belgium', 'Bhutan', 'Bolivia (Plurinational State of)', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Belize', 'Solomon Islands', 'Brunei Darussalam', 'Bulgaria', 'Myanmar', 'Burundi', 'Belarus', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Central African Republic', 'Sri Lanka', 'Chad', 'Chile', 'China', 'Other non-specified areas', 'Colombia', 'Comoros', 'Mayotte', 'Congo', 'Democratic Republic of the Congo', 'Costa Rica', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Benin', 'Denmark', 'Dominican Republic', 'Ecuador', 'El Salvador', 'Equatorial Guinea', 'Ethiopia', 'Eritrea', 'Estonia', 'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia', 'Djibouti', 'Gabon', 'Georgia', 'Gambia', 'State of Palestine', 'Germany', 'Ghana', 'Kiribati', 'Greece', 'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guinea', 'Guyana', 'Haiti', 'Honduras', 'China, Hong Kong SAR', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran (Islamic Republic of)', 'Iraq', 'Ireland', 'Israel', 'Italy', "C\xf4te d'Ivoire", 'Jamaica', 'Japan', 'Kazakhstan', 'Jordan', 'Kenya', "Dem. People's Republic of Korea", 'Republic of Korea', 'Kuwait', 'Kyrgyzstan', "Lao People's Democratic Republic", 'Lebanon', 'Lesotho', 'Latvia', 'Liberia', 'Libya', 'Lithuania', 'Luxembourg', 'China, Macao SAR', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Martinique', 'Mauritania', 'Mauritius', 'Mexico', 'Mongolia', 'Republic of Moldova', 'Montenegro', 'Morocco', 'Mozambique', 'Oman', 'Namibia', 'Nepal', 'Netherlands', 'Cura\xe7ao', 'Aruba', 'New Caledonia', 'Vanuatu', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Norway', 'Micronesia (Fed. States of)', 'Pakistan', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Guinea-Bissau', 'Timor-Leste', 'Puerto Rico', 'Qatar', 'R\xe9union', 'Romania', 'Russian Federation', 'Rwanda', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Viet Nam', 'Slovenia', 'Somalia', 'South Africa', 'Zimbabwe', 'Spain', 'South Sudan', 'Sudan', 'Western Sahara', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syrian Arab Republic', 'Tajikistan', 'Thailand', 'Togo', 'Tonga', 'Trinidad and Tobago', 'United Arab Emirates', 'Tunisia', 'Turkey', 'Turkmenistan', 'Uganda', 'Ukraine', 'TFYR Macedonia', 'Egypt', 'United Kingdom', 'Channel Islands', 'United Republic of Tanzania', 'United States of America', 'United States Virgin Islands', 'Burkina Faso', 'Uruguay', 'Uzbekistan', 'Venezuela (Bolivarian Republic of)', 'Samoa', 'Yemen', 'Zambia', 'WORLD', 'More developed regions', 'Less developed regions', 'AFRICA', 'LATIN AMERICA AND THE CARIBBEAN', 'NORTHERN AMERICA', 'Eastern Asia', 'EUROPE', 'OCEANIA', 'Eastern Africa', 'Middle Africa', 'Northern Africa', 'Southern Africa', 'Western Africa', 'Caribbean', 'Central America', 'South-Eastern Asia', 'South-Central Asia', 'Western Asia', 'Eastern Europe', 'Northern Europe', 'Southern Europe', 'Western Europe', 'Australia and New Zealand', 'Melanesia', 'South America', 'Less developed regions, excluding least developed countries', 'ASIA', 'Least developed countries', 'Sub-Saharan Africa', 'Less developed regions, excluding China', 'Micronesia', 'Polynesia', 'Central Asia', 'Southern Asia',)]
    REGIONS = ('Afghanistan', 'Albania', 'Algeria', 'Angola', 'Antigua and Barbuda', 'Azerbaijan', 'Argentina', 'Australia', 'Austria', 'Bahamas', 'Bahrain', 'Bangladesh', 'Armenia', 'Barbados', 'Belgium', 'Bhutan', 'Bolivia (Plurinational State of)', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Belize', 'Solomon Islands', 'Brunei Darussalam', 'Bulgaria', 'Myanmar', 'Burundi', 'Belarus', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Central African Republic', 'Sri Lanka', 'Chad', 'Chile', 'China', 'Other non-specified areas', 'Colombia', 'Comoros', 'Mayotte', 'Congo', 'Democratic Republic of the Congo', 'Costa Rica', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Benin', 'Denmark', 'Dominican Republic', 'Ecuador', 'El Salvador', 'Equatorial Guinea', 'Ethiopia', 'Eritrea', 'Estonia', 'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia', 'Djibouti', 'Gabon', 'Georgia', 'Gambia', 'State of Palestine', 'Germany', 'Ghana', 'Kiribati', 'Greece', 'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guinea', 'Guyana', 'Haiti', 'Honduras', 'China, Hong Kong SAR', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran (Islamic Republic of)', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Kazakhstan', 'Jordan', 'Kenya', "Dem. People's Republic of Korea", 'Republic of Korea', 'Kuwait', 'Kyrgyzstan', "Lao People's Democratic Republic", 'Lebanon', 'Lesotho', 'Latvia', 'Liberia', 'Libya', 'Lithuania', 'Luxembourg', 'China, Macao SAR', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Martinique', 'Mauritania', 'Mauritius', 'Mexico', 'Mongolia', 'Republic of Moldova', 'Montenegro', 'Morocco', 'Mozambique', 'Oman', 'Namibia', 'Nepal', 'Netherlands', 'Aruba', 'New Caledonia', 'Vanuatu', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Norway', 'Micronesia (Fed. States of)', 'Pakistan', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Guinea-Bissau', 'Timor-Leste', 'Puerto Rico', 'Qatar', 'Romania', 'Russian Federation', 'Rwanda', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Viet Nam', 'Slovenia', 'Somalia', 'South Africa', 'Zimbabwe', 'Spain', 'South Sudan', 'Sudan', 'Western Sahara', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syrian Arab Republic', 'Tajikistan', 'Thailand', 'Togo', 'Tonga', 'Trinidad and Tobago', 'United Arab Emirates', 'Tunisia', 'Turkey', 'Turkmenistan', 'Uganda', 'Ukraine', 'TFYR Macedonia', 'Egypt', 'United Kingdom', 'Channel Islands', 'United Republic of Tanzania', 'United States of America', 'United States Virgin Islands', 'Burkina Faso', 'Uruguay', 'Uzbekistan', 'Venezuela (Bolivarian Republic of)', 'Samoa', 'Yemen', 'Zambia', 'WORLD', 'More developed regions', 'Less developed regions', 'AFRICA', 'LATIN AMERICA AND THE CARIBBEAN', 'NORTHERN AMERICA', 'Eastern Asia', 'EUROPE', 'OCEANIA', 'Eastern Africa', 'Middle Africa', 'Northern Africa', 'Southern Africa', 'Western Africa', 'Caribbean', 'Central America', 'South-Eastern Asia', 'South-Central Asia', 'Western Asia', 'Eastern Europe', 'Northern Europe', 'Southern Europe', 'Western Europe', 'Australia and New Zealand', 'Melanesia', 'South America', 'Less developed regions, excluding least developed countries', 'ASIA', 'Least developed countries', 'Sub-Saharan Africa', 'Less developed regions, excluding China', 'Micronesia', 'Polynesia', 'Central Asia', 'Southern Asia',)

    DEFAULT_DATA_SOURCE = os.path.join(settings.BASE_DIR, 'data', 'WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.csv')

    def __init__(self, storeFilename=os.path.join(settings.BASE_DIR, 'data', 'cache.hdf5')):
        # prepare the filesystem cache
        self.store = pd.HDFStore(storeFilename, complevel=9, complib='blosc')

        # create two dimensional lookup table for extrapolation tables, based on (sex, region) tuples
        self.extrapolationTables = {}

    def readCSV(self, inputCsvFilename=DEFAULT_DATA_SOURCE):
        # UN population by age in single years and sex annually during 1950-2100
        print 'Sourcing CSV...'
        self.data = pd.read_csv(inputCsvFilename)
        print 'done.'

        # -- Change the value of Australia -- #
        self.data.Location = self.data.Location.replace("Australia/New Zealand", "Australia and New Zealand")

        # get list of countries
        #self.regions = pd.unique(self.data.Location).tolist()

    def generateExtrapolationTable(self, sex, region):
        """
        Function that extrapolates the 1st July data to each calender day

        :param region: valid values: anything from 'countries'
        :param sex: valid values: PopFemale, PopMale, PopTotal
        :return: an extrapolation table for the given region/sex tuple
        """
        start = time.clock()
        pop1 = self.data[self.data.Location == region]
        pop1 = pop1[['Time', 'Age', sex]]
        # pop1 = data[['Time', 'Age', SEX]].query('Location' == CNTRY)
        #print pop1

        july1from1950to2100 = [inPosixDays(datetime(y, 7, 1)) for y in xrange(1950, 2100+1)]

        dateRange1970to2100inPosixDays = range(inPosixDays(datetime(1950,1,1)), inPosixDays(datetime(2100,12,31))+1)

        ''' --- Date interpolation function --- '''
        def dateInterp(iage):
            popi = pop1[self.data.Age == iage]
            #popi = pop1[Age == 21] #select particular age COMMENT OUT
            popi = np.asarray(popi[sex])

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
            return (datetime(1970, 1, 1) + timedelta(days=d)).strftime('%Y-%m-%d')
        toDate = np.vectorize(toDate) # vectorize the function to iterate over numpy ndarray
        fullDateRange = toDate(dateRange1970to2100inPosixDays) # 1st result: 1950-01-01

        # Add the fullDateRange to the result1
        table['date1'] = fullDateRange

        # Store the table and get some stats
        self.extrapolationTables[(sex, region)] = table
        generationTime = time.clock() - start
        tableSize = (table.values.nbytes + table.index.values.nbytes + table.columns.values.nbytes) / 1024**2
        print 'Generated extrapolation table for (%s, %s) of size ~%.02fMiB in %.02f seconds' % (sex, region, tableSize, generationTime)

    def storeExtrapolationTable(self, sex, region):
        start = time.clock()
        key = '%s/%s' % (sex, region)
        self.store.put(key, self.extrapolationTables[(sex, region)])
        print 'Stored extrapolation table for (%s, %s) in %.02f seconds' % (sex, region, time.clock()-start)

    def retrieveExtrapolationTable(self, sex, region):
        start = time.clock()
        key = '%s/%s' % (sex, region)
        self.extrapolationTables[(sex, region)] = self.store.get(key)
        print 'Retrieved extrapolation table for (%s, %s) in %.02f seconds' % (sex, region, time.clock()-start)

    def getOrGenerateExtrapolationTable(self, sex, region):
        if (sex, region) not in self.extrapolationTables:
            self.generateExtrapolationTable(sex, region)
        return self.extrapolationTables[(sex, region)]

    def retrieveAllTables(self):
        """
        Loads all tables *into memory*.
        """
        start = time.clock()
        for sex in self.SEXES:
            for region in self.REGIONS:
                self.extrapolationTables[(sex, region)] = self.store.get("%s/%s" % (sex, region))
        print 'Retrieved all extrapolation tables in %.02f seconds' % (time.clock()-start)

    def dayInterpA(self, table, date):
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

    def worldPopulationRankByDate(self, sex, region, dob, date):
        """
        my rank by date: What will be my rank on particular day

        :param sex:
        :param region:
        :param dob:
        :param date:
        :return:
        """
        iAge = inPosixDays(date) - inPosixDays(dob)
        table = self.getOrGenerateExtrapolationTable(sex, region)
        X = self.dayInterpA(table, date)

        # store age and pop in array
        ageArray = np.asarray(X.AGE)
        popArray = np.asarray(X.POP)

        # calc cumulative sum of the population
        cumSum =  np.cumsum(popArray)

        # take the mean of the cumulative sum of the iAge year and preceeding
        rank = np.mean(np.extract((ageArray >= iAge -1) & (ageArray <= iAge), cumSum))
        return long(rank*1000)
