''' 
R to python: yourRank.r

'''
import csv
import numpy as np
import os
import pandas as pd
import glob
from datetime import datetime, timedelta
from time import time
import pylab

from scipy import interpolate
from scipy.interpolate import splrep, InterpolatedUnivariateSpline, interp1d
#from sklearn.linear_model import LinearRegression


#os.path.abspath(__file__)
#folderpath = os.getcwd()

inputData = '../../data/WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.csv'

def main():

	# -- Read in Data --- # 
	# UN population by age in single years and sex annually during 1950-2100 
	data = pd.read_csv(inputData)
	print data.head()

	# store columns to objects:
	Location = data.Location
	Time = data.Time
	Age = data.Age
	PopMale = data.PopMale
	PopFemale = data.PopFemale
	PopTotal = data.PopTotal

	# -- Change the value of Australia -- #
	Location = Location.replace("Australia/New Zealand", "Australia and New Zealand")
	aussie = data[Location == "Australia and New Zealand"]
	#print aussie
			
	# -- Get list of countries -- #
	countries = pd.unique(Location)
	#print countries

	''' --- Date Range Wrangling --- '''
	# -- Date field manipulation: Get date Range, note: Annual data are for the 1st of July -- #
	date_format = '%Y/%m/%d' # define the time format 	#dts = Time.map(lambda x: str(x) + "/07/01")
	# Get the unique years (between 1950 - 2100)
	dts = pd.unique(Time)
	print dts

	# Define function to add July 1st
	def addJuly(d) :
		return datetime.strptime((str(d) + "/07/01"), date_format)
	addJuly = np.vectorize(addJuly) # vectorize the function to iterate over numpy ndarray
	dts = addJuly(dts) # 1st result: " datetime.datetime(1950, 7, 1, 0, 0) "
	print dts

	# Define function to get Date as numeric
	refDate = datetime.strptime('1970/01/01', date_format)
	def numDate(d):
		return (d - refDate).days # get back "days" by calling .days object
	numDate = np.vectorize(numDate) # vectorize the function to iterate over numpy ndarray
	date2 = numDate(dts) # 1st result: -7124
	print date2

	# Define the FULL range from 1st of Jan 1950 to 31st dec 2100 store in array
	date2Min = np.min(date2)
	date2Max = np.max(date2)
	dateLowest = date2Min - ((date2Min) - numDate(datetime.strptime('1950/01/01', date_format))) 
	dateHighest = (numDate(datetime.strptime('2100/12/31', date_format)) - date2Max) + date2Max
	#xout = []
	xout = [dateLowest, dateHighest]
	print xout


	''' --- function that extrapolates the 1st July data to each calendar day --- '''
	# Sex names in the Data
	SEXnames = data.columns.values
	holder = []
	for headers in SEXnames:
		if "Pop" in headers:
			#print headers
			holder.append(headers)
	SEXnames = holder
	print SEXnames

	# AGE in days refering to the annual data - we assume that the average age of one years old is 1 years and 183 days
	age3 = range(0,100)
	age3 = [ x*365+183 for x in age3]

	# Range of days (age)
	ageout = range(0, 36501)

	''' --- function doitall() start --- '''
	# Function that extrapolates the 1st July data to each calender day
	def doitall(CNTRY, iSEX, RESULT):
		SEX = SEXnames[iSEX] # iSEX will be and index number
		print SEX

		pop1 = data[Location == CNTRY]
		pop1 = pop1[['Time', 'Age', SEX]]
		# pop1 = data[['Time', 'Age', SEX]].query('Location' == CNTRY) 
		print pop1

		''' --- Date interpolation function --- '''
		def dateInterp(iage):
			popi = pop1[Age == iage]
			#popi = pop1[Age == 21] #select particular age COMMENT OUT
			popi = np.asarray(popi[SEX])
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
		print result1.head # results: "age_0, age_1, ..."

		# Convert the numerical days to date string
		days= range(xout[0], xout[1]+1) # the full date range in days from 1970/01/01 - 2100/12/31
		def toDate(d):
			return (refDate + timedelta(days=d)).strftime('%Y-%m-%d') 
		toDate = np.vectorize(toDate) # vectorize the function to iterate over numpy ndarray
		fullDateRange = toDate(days) # 1st result: 1950-01-01

		# Add the fullDateRange to the result1
		result1['date1'] = fullDateRange
		print result1['date1']

		# End the doitall function
		if (RESULT == 0):
			result1.to_csv(CNTRY+SEX+".csv")
			return result1
		else:
			return result1

	# Examples
	CNTRY = "WORLD"
	iSEX = 2
	RESULT = 1
	#doitall(CNTRY, iSEX, RESULT)
	pop2 = doitall(CNTRY, iSEX, RESULT)

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
		iuspl2 =  InterpolatedUnivariateSpline(age3, popi/365)
		iuspl2_pred = iuspl2(ageout)

		# the output
		col1 =  pd.DataFrame(ageout, columns=['AGE'])
		col2 = pd.DataFrame(iuspl2_pred, columns = ['POP'])
		#print col1, col2
		merged = col1.join(col2)
		#print merged
		#return pd.DataFrame(ageout, iuspl2_pred, columns=['AGE', 'POP'])
		return merged

	# example
	#dayInterpA('1950-01-05')


	
	''' --- function: my rank by age --- '''
	# def match function and toDate  
	#match = lambda a, b: [ b.index(x)+1 if x in b else None for x in a ]
	toDate = lambda d: (refDate + timedelta(days=d)).strftime('%Y-%m-%d') 

	# what will be my rank when I am aged xxx days
	def yourRANKbyAge (DoB, iAge):
		DoB = datetime.strptime(DoB, date_format)
		DATE = numDate(DoB) + iAge # returns the numerical date from 1970/01/01
		DATE = toDate(DATE)
		X = dayInterpA(DATE) # CHECK IF THIS CAN TAKE BOTH DATE AND NUMERIC FORMAT!!!
		#print X

		# store age and pop in array
		ageArray = np.asarray(X.AGE)
		popArray = np.asarray(X.POP)

		# calc cumulative sum of the population
		cumSum =  np.cumsum(popArray)
		#print cumSum

		# take the mean of the cumulative sum of the iAge year and preceeding
		RANK = np.mean(np.extract((ageArray >= iAge -1) & (ageArray <= iAge), cumSum))
		return RANK
		#print RANK 

	#yourRANKbyAge('1993/12/06', 3650)


	''' --- function: my rank by date --- '''
	# my rank by date: What will be my rank on particular day
	def yourRANKbyDate(DoB, DATE):
		DoB = datetime.strptime(DoB, date_format) 	# your date of birth
		DATE = DATE 	# any input date
		#print DATE
		iAge = numDate(datetime.strptime(DATE, '%Y-%m-%d')) - numDate(DoB) 
		#print iAge
		X = dayInterpA(DATE) 
		#print X

		# store age and pop in array
		ageArray = np.asarray(X.AGE)
		popArray = np.asarray(X.POP)

		# calc cumulative sum of the population
		cumSum =  np.cumsum(popArray)
		#print cumSum

		# take the mean of the cumulative sum of the iAge year and preceeding
		RANK = np.mean(np.extract((ageArray >= iAge -1) & (ageArray <= iAge), cumSum))
		return RANK
		#print RANK 

	#yourRANKbyDate('1993/12/06', '2001-09-11')

	''' --- function: my rank today --- '''
	# what is myrank today
	def yourRANKToday(DoB):
		DoB = datetime.strptime(DoB, date_format) 	# your date of birth

		# get time now
		now = datetime.now()
		today = now.strftime('%Y-%m-%d')
		iAge = numDate(datetime.strptime(today, '%Y-%m-%d')) - numDate(DoB)

		# interpolate values for that day
		X = dayInterpA(today)

		# store age and pop in array
		ageArray = np.asarray(X.AGE)
		popArray = np.asarray(X.POP)

		# calc cumulative sum of the population
		cumSum =  np.cumsum(popArray)
		#print cumSum

		# take the mean of the cumulative sum of the iAge year and preceeding
		RANK = np.mean(np.extract((ageArray >= iAge -1) & (ageArray <= iAge), cumSum))
		return RANK
		#print RANK 

	#yourRANKToday('1993/12/06') 
	

	''' --- function: your rank tomorrow --- '''
	# finding the date for specific rank
	def yourRANKTomorrow(birth, wRank):
		# The date of the study
		final_time = '2100/01/01'
		# The number of years from input birth to '2100/01/01'
		length_time = relativedelta(datetime.strptime(final_time, date_format) , datetime.strptime(birth, date_format)).years

		# Make sure that difference between DOB and final Date > 100
		if length_time < 100:
			l_max = np.round(length_time)
		else:
			l_max = 100

		xx = []
		for jj in range(1, (len(range(10, l_max+10, 10))+1)):
			try:
				xx.append(yourRANKbyAge(DoB = birth, iAge= (jj*3650)))
			except Exception:
				print "Breaks the function if either the birthdate is too late \
				for some rank or the rank is too high for some birthdate"
				pass

		# check the array for NaN?
		xx = np.array(xx) # convert xx from list to array
		nanIndex = np.where(np.isnan(xx)) # return array of index positions for NANs

		''' NEED TO BREAK THE FUNCTION IF CC IS TRUE - NOT YET IMPLEMENTED '''
		# check to see if all of the Ranks are less than the wRank
		cc = np.all(xx < wRank)
		if cc == True:
			print "You are too young"
			#break 

		# now find the interval containing wRank
		Upper_bound =  (np.amin(np.where((xx < wRank) == False))+1)*10 # +1 because of zero index
		Lower_bound = Upper_bound-10

		# Define new range
		range_2 = np.arange(Lower_bound-2, Upper_bound+1) # +1 due to zero index

		# locate the interval 
		xx_ = np.zeros((len(range_2),2))

		# given that interval, do a yearly interpolation
		for kk in range_2:
			xx_[(kk - np.amin(range_2)),0] = yourRANKbyAge(DoB=birth,iAge=kk*365)
			xx_[(kk - np.amin(range_2)),1] = kk*365

		# Search again for the yearly interval containing wRank
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
  		final_date = toDate(numDate(datetime.strptime(birth, date_format)) + final_age )
  		# print final_age, final_date

  		''' CHECK THESE INTERPOLATION VALUES '''
  		#now we also want to plot our life-path, so we do spline interpolation for the stuff we calculated in the first step
 		# (i.e. the ranks over decades) and interpolate using bSplines.
 		xx_interp = InterpolatedUnivariateSpline((np.arange(10, l_max+1, 10)*365),xx)
 		# print xx_interp
 		x_interp = xx_interp((np.arange(1,36501,365)))
 		# print x_interp

 		# find the rank nearest to wRank
 		find_r = np.amin(np.where(abs(x_interp - wRank)))
 		# print find_r

 		# The value this function returns
 		exactAge =round(final_age/365, 1)
 		age = math.floor(final_age/365)
 		DATE = final_date
 		
 		return pd.DataFrame({'exactAge': pd.Series([exactAge], index = ['1']), 'age': pd.Series([age],index = ['1']), 'DATE': pd.Series([DATE], index = ['1'])})

	RES = yourRANKTomorrow('1993/12/06', 7000000)


	''' --- LIFE EXPECTANCY --- '''
	#read data for life expectancy: male=1,female=2,both=3
	life_expectancy_ages = pd.read_csv("life_expectancy_ages.csv")

	# What is the life expectancy on when I reach specific RANK speRANK 
	le_exact_age = RES.exactAge 
	le_age =  RES.age
	le_date = RES.DATE

	#For which CNTRY AND SEX DO YOU WANT TO KNOW THE REMAINING LIFE EXPECTANCY AT CERTAIN TIME/AGE
	CNTRY1 = "WORLD"
	iSEX1 = 2 #male=0,female=1,both=2

	

if __name__ == '__main__':
	main()


















