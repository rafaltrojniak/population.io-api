''' 
R to python: yourRank.r

'''
import csv
import numpy as np
import os
import pandas as pd
import glob
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from time import time
import pylab
import math
from scipy import interpolate
from scipy.interpolate import splrep, InterpolatedUnivariateSpline, interp1d

inputData = '../../data/WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.csv'
inputLifeExpectancy = '../../data/life_expectancy_ages.csv'

def main():
    # -- Read in Data --- # 
    # UN population by age in single years and sex annually during 1950-2100 
    data = pd.read_csv(inputData)
    print(data.head())

    # store columns to objects:
    Location = data.Location
    Time = data.Time
    Age = data.Age

    # -- Change the value of Australia -- #
    Location = Location.replace("Australia/New Zealand", "Australia and New Zealand")
    aussie = data[Location == "Australia and New Zealand"]

    # -- Get list of countries -- #
    countries = pd.unique(Location)

    ''' --- Date Range Wrangling --- '''
    # -- Date field manipulation: Get date Range, note: Annual data are for the 1st of July -- #
    date_format = '%Y/%m/%d' # define the time format   #dts = Time.map(lambda x: str(x) + "/07/01")
    dts = pd.unique(Time)

    # --- Define function to add July 1st --- #
    def addJuly(d) :
        return datetime.strptime((str(d) + "/07/01"), date_format)
    addJuly = np.vectorize(addJuly) 
    dts = addJuly(dts) # 1st result: " datetime.datetime(1950, 7, 1, 0, 0) "

    # --- Define function to get Date as numeric --- #
    refDate = datetime.strptime('1970/01/01', date_format)
    def numDate(d):
        return (d - refDate).days 
    numDate = np.vectorize(numDate) 
    date2 = numDate(dts) # 1st result: -7124

    # --- Define the FULL range from 1st of Jan 1950 to 31st dec 2100 store in array --- #
    date2Min = np.min(date2)
    date2Max = np.max(date2)
    dateLowest = date2Min - ((date2Min) - numDate(datetime.strptime('1950/01/01', date_format))) 
    dateHighest = (numDate(datetime.strptime('2100/12/31', date_format)) - date2Max) + date2Max
    xout = [dateLowest, dateHighest]

    ''' --- function that extrapolates the 1st July data to each calendar day --- '''
    # --- Sex names in the Data --- #
    SEXnames = data.columns.values
    holder = []
    for headers in SEXnames:
        if "Pop" in headers:
            holder.append(headers)
    SEXnames = holder
    print(SEXnames)

    # AGE in days refering to the annual data - we assume that the average age of one years old is 1 years and 183 days
    age3 = range(0,100)
    age3 = [ x*365+183 for x in age3]

    # Range of days (age)
    ageout = range(0, 36501)

    ''' --- function doitall() start --- '''
    # --- Function that extrapolates the 1st July data to each calender day --- #
    def doitall(CNTRY, iSEX, RESULT):
        # --- Which sex: male or female --- #
        SEX = SEXnames[iSEX] 
        # --- Which country --- #
        pop1 = data[Location == CNTRY]
        pop1 = pop1[['Time', 'Age', SEX]]

        ''' --- Date interpolation function --- '''
        days= range(xout[0], xout[1]+1)        
        def dateInterp(iage):
            popi = np.asarray(pop1.loc[Age == iage.name, SEX])
                
            # spline interpolation function from Scipy Package
            iuspl = InterpolatedUnivariateSpline(date2, popi, k=4)
            return iuspl(days)

        # --- store the results of the date interpolation --- #
        result1 = pd.DataFrame(index = range(0,len(days)), columns = range(0,100))
        result1 = result1.apply(dateInterp, axis=0)        
        
        # --- Change column names by appending "age_" --- #
        oldHeaders = result1.columns
        newHeaders = []
        for i in oldHeaders:
            newHeaders.append("age" + "_" + str(i))
        result1.columns = newHeaders
        #print(result1.head) # results: "age_0, age_1, ..."

        # --- Convert the numerical days to date string --- #
        # the full date range in days from 1970/01/01 - 2100/12/31
        days= range(xout[0], xout[1]+1) 
        def toDate(d):
           return (refDate + timedelta(days=d)).strftime('%Y/%m/%d') 
        #toDate = np.vectorize(toDate) 
        #fullDateRange = toDate(days) # 1st result: 1950-01-01
        fullDateRange = len(days)*[None]
        for i in range(0,len(days)):
            fullDateRange[i] = toDate(days[i])

        # --- Add the fullDateRange to the result1 --- #
        result1['date1'] = fullDateRange
        #print(result1['date1'])

        # --- End the doitall function --- #
        if (RESULT == 0):
            result1.to_csv(CNTRY+SEX+".csv")
            return result1
        else:
            return result1
    # Examples
    CNTRY = "World"
    iSEX = 2
    RESULT = 1
    #doitall(CNTRY, iSEX, RESULT)
    pop2 = doitall(CNTRY, iSEX, RESULT)

    ''' --- function that interpolates age in days -- '''
    def dayInterpA(iDate):
        # --- age 0 to 99 --- #
        popi = pop2[pop2.date1 == iDate]

        # --- Remove the columns for age 100 and the date1 --- #       
        popi = popi.iloc[:,0:100]

        # store the popi results into an array for the interpolation
        popi = np.asarray(popi)

        # Interpolate the age in Days
        iuspl2 =  InterpolatedUnivariateSpline(age3, popi/365)
        iuspl2_pred = iuspl2(ageout)

        # the output
        merged = pd.DataFrame(index = range(0,len(ageout)), columns = ['AGE','POP'])
        merged['AGE'] = ageout
        merged['POP'] = iuspl2_pred
        return merged

    
    ''' --- function: my rank by age --- '''
    # def match function and toDate  
    toDate = lambda d: (refDate + timedelta(days=d)).strftime('%Y/%m/%d') 

    # what will be my rank when I am aged xxx days
    def yourRANKbyAge (DoB, iAge):
        DoB = datetime.strptime(DoB,'%Y-%m-%d' ).strftime(date_format)
        DoB = datetime.strptime(DoB, date_format)
        DATE = numDate(DoB) + iAge # returns the numerical date from 1970/01/01
        DATE = toDate(int(DATE))
        X = dayInterpA(DATE) # CHECK IF THIS CAN TAKE BOTH DATE AND NUMERIC FORMAT!!!

        # store age and pop in array
        ageArray = np.asarray(X.AGE)
        popArray = np.asarray(X.POP)

        # calc cumulative sum of the population
        cumSum =  np.cumsum(popArray)

        # take the mean of the cumulative sum of the iAge year and preceeding
        RANK = np.mean(np.extract((ageArray >= iAge -1) & (ageArray <= iAge), cumSum))
        return RANK

    ''' --- function: my rank by date --- '''
    # my rank by date: What will be my rank on particular day
    def yourRANKbyDate(DoB, DATE):
        DoB = datetime.strptime(DoB,'%Y-%m-%d' ).strftime(date_format)
        DATE = datetime.strptime(DATE,'%Y-%m-%d' ).strftime(date_format)
        
        DoB = datetime.strptime(DoB, date_format)   # your date of birth
        DATE = DATE     # any input date

        # --- interpolated age --- #
        iAge = numDate(datetime.strptime(DATE,  date_format)) - numDate(DoB) 
        X = dayInterpA(DATE) 

        # store age and pop in array
        ageArray = np.asarray(X.AGE)
        popArray = np.asarray(X.POP)

        # calc cumulative sum of the population
        cumSum =  np.cumsum(popArray)

        # take the mean of the cumulative sum of the iAge year and preceeding
        RANK = np.mean(np.extract((ageArray >= iAge -1) & (ageArray <= iAge), cumSum))
        return RANK

    ''' --- function: my rank today --- '''
    # what is myrank today
    def yourRANKToday(DoB):
        DoB = datetime.strptime(DoB,'%Y-%m-%d' ).strftime(date_format)
        DoB = datetime.strptime(DoB, date_format) 

        # get time now
        now = datetime.now()
        today = now.strftime('%Y/%m/%d')
        iAge = numDate(datetime.strptime(today,  date_format)) - numDate(DoB)

        # interpolate values for that day
        X = dayInterpA(today)

        # store age and pop in array
        ageArray = np.asarray(X.AGE)
        popArray = np.asarray(X.POP)

        # calc cumulative sum of the population
        cumSum =  np.cumsum(popArray)

        # take the mean of the cumulative sum of the iAge year and preceeding
        RANK = np.mean(np.extract((ageArray >= iAge -1) & (ageArray <= iAge), cumSum))
        return RANK


    DoB = '1993-12-06'
    
    yourRANKToday(DoB) #my ranking today: 2591260
    yourRANKbyAge(DoB=DoB,iAge=3650) #my ranking when I was 10 years old (3650 days) : 1209884
    yourRANKbyDate(DoB,'2001-09-11') #my ranking on 11th Sept 2001 :941006



    ''' --- function: your rank tomorrow --- '''
    # finding the date for specific rank
    def yourRANKTomorrow(birth, wRank):
        # The date of the study
        final_time = '2100/01/01'
        # The number of years from input birth to '2100/01/01'
        length_time = relativedelta(datetime.strptime(final_time, date_format) , datetime.strptime(birth, '%Y-%m-%d')).years

        # Make sure that difference between DOB and final Date < 100
        if length_time < 100:
            #l_max = np.round(length_time)
            l_max = int(np.floor(length_time/10)*10)
        else:
            l_max = 100

        xx = []
        for jj in range(1, (len(range(10, l_max+10, 10))+1)):
            try:
                xx.append(yourRANKbyAge(DoB = birth, iAge= (jj*3650)))
            except Exception:
                print("Breaks the function if either the birthdate is too late \
                for some rank or the rank is too high for some birthdate")
                pass

        # check the array for NaN?
        xx = np.array(xx) # convert xx from list to array
        nanIndex = np.where(np.isnan(xx)) # return array of index positions for NANs

        ''' NEED TO BREAK THE FUNCTION IF CC IS TRUE - NOT YET IMPLEMENTED '''
        # check to see if all of the Ranks are less than the wRank
        cc = np.all(xx < wRank)
        if cc == True:
            print("You are too young")
            return [None]

        
        
        # now find the interval containing wRank
        Upper_bound =  (np.amin(np.where((xx < wRank) == False))+1)*10 # +1 because of zero index
        Lower_bound = Upper_bound-10
        
        if xx[1]>wRank:
            Lower_bound = 2

        # Define new range
        range_2 = np.arange(Lower_bound-2, Upper_bound+1) # +1 due to zero index

        # locate the interval 
        xx_ = np.zeros((len(range_2),2))

        # given that interval, do a yearly interpolation
        for kk in range_2:
            xx_[(kk - np.amin(range_2)),0] = yourRANKbyAge(DoB=birth,iAge=kk*365)
            xx_[(kk - np.amin(range_2)),1] = kk*365

        # Search again for the yearly interval containing wRank
        #Upper_bound =   xx_[np.amin(np.where((xx_[:,0] < wRank) == False)),1]
        #Lower_bound = xx_[np.amax(np.where((xx_[:,0] < wRank) == True)),1]
        if xx_[1,0]>wRank:
            Lower_bound = 0
            Upper_bound = xx_[-1,1]
        else:
            Upper_bound =   xx_[np.amin(np.where((xx_[:,0] < wRank) == False)),1]
            Lower_bound = xx_[np.amax(np.where((xx_[:,0] < wRank) == True)),1]

        range_3 = np.arange(Lower_bound, Upper_bound+1)
        #print (range_3)

        xx_ = np.zeros((len(range_3),2))

        # From this point on, this stuff is within a year (daily), due to the fact that the evolution of the rank is linear
        # we do linear interpolation to get the exact day faster
        end_point = range_3[len(range_3)-1]
        first_point = range_3[0]
        # print end_point, first_point

        # Get the rank for the first and last days in range_3
        rank_end = yourRANKbyAge(DoB = birth, iAge = end_point)
        rank_first = yourRANKbyAge(DoB = birth, iAge = first_point)

        # This gives us the age when we reach wRank and the exact date
        final_age = np.interp(wRank, [rank_first, rank_end], [Lower_bound, Upper_bound])
        final_date = toDate(numDate(datetime.strptime(birth, '%Y-%m-%d')) + final_age )
        # print final_age, final_date

        ''' CHECK THESE INTERPOLATION VALUES '''
        #now we also want to plot our life-path, so we do spline interpolation for the stuff we calculated in the first step
        # (i.e. the ranks over decades) and interpolate using bSplines.
        xx_interp = InterpolatedUnivariateSpline((np.arange(10, l_max+1, 10)*365),xx,k=4)
        # print xx_interp
        x_interp = xx_interp((np.arange(1,36501,365)))
        # print x_interp

        # find the rank nearest to wRank
        #find_r = np.amin(np.where(abs(x_interp - wRank)))
        find_r = np.where(abs(x_interp-wRank)==np.min(abs(x_interp-wRank)))[0][0]
        # print find_r

        # The value this function returns
        exactAge =round(final_age/365, 1)
        age = math.floor(final_age/365)
        DATE = datetime.strptime(final_date,date_format ).strftime('%Y-%m-%d')
        
        return pd.DataFrame({'exactAge': pd.Series([exactAge], index = ['1']), 'age': pd.Series([age],index = ['1']), 'DATE': pd.Series([DATE], index = ['1'])})

    
    
    
    RES = yourRANKTomorrow('1990-12-06', 7000000)


    ''' --- LIFE EXPECTANCY --- '''
    DoB = "1993-12-06"
    speRANK = 7000000
    #read data for life expectancy: male=0,female=1
    life_expectancy_ages = pd.read_csv(inputLifeExpectancy)
    print(life_expectancy_ages.columns)
    # What is the life expectancy on when I reach specific RANK speRANK 
    le_exact_age = RES.exactAge[0] 
    le_age =  RES.age[0]
    le_date = RES.DATE[0]

    # For which CNTRY AND SEX DO YOU WANT TO KNOW THE REMAINING LIFE EXPECTANCY AT CERTAIN TIME/AGE
    CNTRY1 = "World"
    iSEX1 = 1 

    ''' --- rem_le function ---'''
    def rem_le(CNTRY1, iSEX1, le_date):
        #le_date = datetime.strptime(le_date,'%Y-%m-%d' ).strftime(date_format)
        
        # find beginning of 5 yearly period for the le_date
        le_yr = datetime.strptime(le_date,'%Y-%m-%d').year
        lowest_year = math.floor(int(le_yr)/5)*5
        # print le_yr, lowest_year

        #extract a row corresponding to the time-period
        life_exp_prd_5below = life_expectancy_ages[(life_expectancy_ages.region == CNTRY1) & (life_expectancy_ages.sex == iSEX1) & (life_expectancy_ages.Begin_prd == lowest_year-5)]
        life_exp_prd_ext = life_expectancy_ages[(life_expectancy_ages.region == CNTRY1) & (life_expectancy_ages.sex == iSEX1) & (life_expectancy_ages.Begin_prd == lowest_year)]
        life_exp_prd_5above = life_expectancy_ages[(life_expectancy_ages.region == CNTRY1) & (life_expectancy_ages.sex == iSEX1) & (life_expectancy_ages.Begin_prd == lowest_year+5)]

        # life_exp_prd - notice change from 7 to 4
        life_exp_prd = pd.concat([life_exp_prd_5below, life_exp_prd_ext, life_exp_prd_5above])
        life_exp_prd = life_exp_prd.ix[:,4:len(life_exp_prd.columns)]

        # Place holder for Agenames and values for three consecutive periods of interest
        life_exp_ = np.zeros((len(life_exp_prd.columns), 4))

        # Age group starting at and less than the next value: 0, 1, 5, 10 
        life_exp_[:,0] =  np.insert((np.arange(5, 130, 5)), 0, [0,1])

        # transpose the dataframe - prep for assinging life expectancy vals
        life_exp_prd = life_exp_prd.T 
      
        # Assigning life expectancy values
        life_exp_[:,1] = life_exp_prd[life_exp_prd.columns[0]].values
        life_exp_[:,2]  = life_exp_prd[life_exp_prd.columns[1]].values
        life_exp_[:,3]  = life_exp_prd[life_exp_prd.columns[2]].values

        # interpolations
        # --- ADDED (np.amax(max(np.where(life_exp_[:,1] == 0))))
        xx_interp1 = InterpolatedUnivariateSpline(life_exp_[:,0],life_exp_[:,1] )
        xx_interp2 = InterpolatedUnivariateSpline(life_exp_[:,0],life_exp_[:,2] )
        xx_interp3 = InterpolatedUnivariateSpline(life_exp_[:,0],life_exp_[:,3] )

        # predictions
        x_interp1 = xx_interp1(le_exact_age)#interpolated value for AGE in earlier 5 yearly period
        x_interp2 = xx_interp2(le_exact_age)#interpolated value for AGE in the 5 yearly period of interest
        x_interp3 = xx_interp3(le_exact_age)#interpolated value for AGE in 5 yearly period after
        
        # matrix of vals
        life_exp_yr = np.zeros((3,2))

        #The mid point of period 2010-2015 which is from 1st July 2010 to June 30 of 2015, therefore, the mid point is 1st Jan 2013
        #In the following we turn the year to the date and then to numeric. We will use these to interpolate between periods and then predict the le for exact date 
        addDate = lambda d: numDate(datetime.strptime(str(int(d)+3) + "/01/01", date_format))


        life_exp_yr[:,0] = [addDate(lowest_year-5), addDate(lowest_year), addDate(lowest_year+5) ]
        life_exp_yr[:,1] = [x_interp1, x_interp2, x_interp3]
        #print(life_exp_yr)
        life_exp_spl = InterpolatedUnivariateSpline(life_exp_yr[:,0],life_exp_yr[:,1],k=2)
        return life_exp_spl(numDate(datetime.strptime(le_date, '%Y-%m-%d'))) 

    ''' --- continuing the example --- '''
    x_interp = rem_le(CNTRY1=CNTRY1,iSEX1=iSEX1,le_date=le_date) 

    # --- calc the date of death --- # 
    dateOfDeath = lambda d: ((datetime.strptime(le_date, '%Y-%m-%d')) + timedelta(days=d)).strftime('%Y-%m-%d')  

    print("You, born in " + str(DoB) + " will reach " + str(speRANK*1000) + "th person in " \
    + str(CNTRY) + " on "+ str(le_date) + " and you will be " + str(le_age) + " years old. As a " \
    + str(iSEX1) + " " + str(CNTRY1) + " citizen, you will still have" + str(np.round(x_interp,2)) \
    + " years to live. And your expected date of death is " + str(dateOfDeath(x_interp*365)))


    #Test cases - Samir
    #e.g.:
    CNTRY = 'World' # as named in new lstcntry#KC#
    iSEX = 2 # 0= Males, 1 = Females, and 2 = Both Sexes
    pop2 = doitall(CNTRY=CNTRY,iSEX=iSEX, RESULT = 1) #if RESULT = 0 then this function will save a ~93mb file in csv 
    
    DoB = "1993-12-06"
    #The following values for the corresponding example of DoB keeps changing as we run this on different date#KC#
    yourRANKToday(DoB) 
    yourRANKbyAge(DoB=DoB,iAge=3650) #my ranking when I was 10 years old 
    yourRANKbyDate(DoB,"2001-09-11") #my ranking on 11th Sept 2001 
    
    
    DoB = "1920-01-01"
    #Just to test errors:
    #yourRANKbyDate(DoB,"1949/12/31") #my ranking on 31st Dec 1949 :ERROR Data not available 
    yourRANKbyDate(DoB,"1950-01-01") #1506711 #my ranking on 1st Jan 1950: minimum Date for which rank can be reported
    
    yourRANKbyDate(DoB,"2020-01-01") #NA #my ranking on 1st Jan 2020: 
    yourRANKbyDate(DoB,"2019-12-09") #NA #if you are more than 36500 days older then you are too old to report exact rank
    
    
    DoB = "2020-12-31"
    yourRANKToday(DoB) #NA #because the person is not born yet
    yourRANKbyDate(DoB,"2021-12-31") #133045.1
    
    DoB = "2100-12-31" #maximum DoB
    yourRANKToday(DoB) #NA
    yourRANKbyDate(DoB,"2100-12-31") #349.4013 #Also maximum Date that a rank can be reported...
    
    DoB = "1920-1-1" #minimum DoB (it is possible for DoB few years earlier but I suggest to start at 1920, for older cohorts, we put a message that the person is too old for and report the rank of the person born on 1920/1/1, saying your rank is higher than the rank for 1920/1/1 )
    yourRANKToday(DoB) #7265259
    yourRANKbyDate(DoB,"2100-12-31") #NA
    
    
    ###Test for other country####
    CNTRY = 'Austria' # as named in new lstcntry#KC#
    iSEX = 0 # 1= Males, 2 = Females, and 3 = Both Sexes
    pop2 = doitall(CNTRY,iSEX, RESULT = 1) #if RESULT = 0 then this function will save a ~93mb file in csv 
    
    DoB = '1983-12-19'
    yourRANKToday(DoB) #my ranking today: 1472 
    yourRANKbyAge(DoB=DoB,iAge=3650) #my ranking when I was 10 years old (3650 days) : 481
    yourRANKbyDate(DoB,"2001-09-11") #my ranking on 11th Sept 2001 :827.4809
    
    speRANK = 2000 #specific rank
    RES = yourRANKTomorrow(DoB,speRANK)
    le_exact_age =  RES.exactAge[0] #exact age in years in two decimals to reach speRANK 40.12
    le_age =  RES.age[0] # age in years to reach speRANK: 40
    le_date = RES.DATE[0] # date to reach speRANK: "2024-01-20"
    x_interp = rem_le(CNTRY1=CNTRY,iSEX1=1,le_date=RES.DATE[0])
    x_interp # 44.68
    print("You, born in " + str(DoB) + " will reach " + str(speRANK*1000) + "th person in " \
    + str(CNTRY) + " on "+ str(le_date) + " and you will be " + str(le_age) + " years old. As a " \
    + str(iSEX) + " " + str(CNTRY) + " citizen, you will still have" + str(np.round(x_interp,2)) \
    + " years to live. And your expected date of death is " + str(dateOfDeath(x_interp*365)))

    
    ###Test 3rd country#######
    CNTRY = 'India' # as named in new lstcntry#KC#
    iSEX = 1 # 1= Males, 2 = Females, and 3 = Both Sexes
    pop2 = doitall(CNTRY=CNTRY,iSEX=iSEX, RESULT = 1) #if RESULT = 0 then this function will save a ~93mb file in csv 
    
    DoB = '1984-01-06'
    yourRANKToday(DoB) #my ranking today: 344670.4 
    yourRANKbyAge(DoB=DoB,iAge=3650) #my ranking when I was 10 years old (3650 days) : 113045.3
    yourRANKbyDate(DoB,'2001-09-11') #my ranking on 11th Sept 2001 :199842.8
    
    speRANK = 500000 #specific rank
    RES = yourRANKTomorrow(DoB,speRANK)
    le_exact_age =  RES.exactAge[0] #exact age in years in two decimals to reach speRANK 45.12
    le_age =  RES.age[0] # age in years to reach speRANK: 45
    le_date = RES.DATE[0] # date to reach speRANK: "2062-07-25"
    x_interp = rem_le(CNTRY1=CNTRY,iSEX1=iSEX+1,le_date=RES.DATE[0])
    x_interp # 33.15
    print("You, born in " + str(DoB) + " will reach " + str(speRANK*1000) + "th person in " \
    + str(CNTRY) + " on "+ str(le_date) + " and you will be " + str(le_age) + " years old. As a " \
    + str(iSEX) + " " + str(CNTRY) + " citizen, you will still have" + str(np.round(x_interp,2)) \
    + " years to live. And your expected date of death is " + str(dateOfDeath(x_interp*365)))
 


if __name__ == '__main__':
    main()

