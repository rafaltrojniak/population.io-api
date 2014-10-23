import csv
import os, sys
import pandas as pd
import numpy as np 
from datetime import datetime
import time
import math
from scipy import interpolate
#import matplotlib.pyplot as plt
from scipy.interpolate import splrep, InterpolatedUnivariateSpline, UnivariateSpline

# round data to nearest 5 year time window
def rounddown(x, base=5):
    return int(base * math.floor(float(x)/base))
# Get timedelta
def setInterpDate(x, offset):
    idate = datetime.strptime(str(x+offset+3)+"/1"+"/1", "%Y/%m/%d")
    return (idate - datetime(1970, 1, 1)).days
# generic days since epoch
def daysSinceEpoch(x, format="%Y-%m-%d"):
    idate = datetime.strptime(x,format)
    return (idate - datetime(1970, 1, 1)).days

# Import data
data = pd.read_csv('../../data/Survival_ratio_Cohort_ages.csv', header=0)

# --- wrap in function --- #
# get columns which correspond to the inputs
def dist_odata(cntry, sex, idate, iage):
    iyear = int(idate[0:4])
    flr_yr = rounddown(iyear, base=5)
    #print(iyear, flr_yr)

    # get closest age in 5 year windows
    flr_age = rounddown(iage, base=5)
    #print(flr_age)

    # Get the age cohort
    if flr_age>=5:
        cohort_st = list(data.columns).index("X"+str(flr_age-5))
    else:
        cohort_st = 4
    cohort_end = len(data.columns)
    #cohort = data.ix[:,cohort_st:cohort_end]
    cohort = data.loc[(data.region==cntry) & (data.sex==sex) & (data.Begin_prd >=(flr_yr-5))].ix[:,cohort_st:cohort_end]
    #print(cohort.columns)

    # get older and younger cohort
    cohort_old = data.loc[(data.region==cntry) & (data.sex==sex) & (data.Begin_prd >=(flr_yr-10))].ix[:,cohort_st:cohort_end]
    cohort_young = data.loc[(data.region==cntry) & (data.sex==sex) & (data.Begin_prd >=(flr_yr))].ix[:,cohort_st:cohort_end]

    # get dates for the jan 1st for 3 years --> then to Unix timestamp
    dates = [setInterpDate(flr_yr, -5), setInterpDate(flr_yr,0), setInterpDate(flr_yr,+5)]
    #print(dates)

    # make the output datatable
    temp = np.zeros(shape=(len(cohort.columns),7))
    odata = pd.DataFrame(temp, columns=["lower_age","pr0","pr1","pr2","pr_sx_date","death_percent","dth_pc_after_exact_age"])

    # fill in with existing values
    if iage>=5:
        odata['lower_age'] =np.arange(iage-5, 130, 5)
    else:
        odata['lower_age'] =np.arange(0, 130, 5)
    odata['pr0'] = np.matrix(cohort_old).diagonal().T
    odata['pr1'] = np.matrix(cohort).diagonal().T
    odata['pr2'] = np.matrix(cohort_young).diagonal().T

    # Interpolate for the input date (idate)
    odata["pr_sx_date"] = np.array([InterpolatedUnivariateSpline(dates,list(odata.ix[i,1:4]),k=2)(daysSinceEpoch(idate)) for i in np.arange(0, len(cohort.columns),1)])


    clen = len(odata)
    # calc the % deaths
    # odata["death_percent"][0] = 0
    odata["death_percent"][1] = 100
    #odata["death_percent"][2:clen] = [((odata["death_percent"][i-1])*(odata["pr_sx_date"][i-1])) for i in np.arange(2,clen,1) ]
    for i in np.arange(2,clen,1):
        odata["death_percent"][i] = odata["death_percent"][i-1]*odata["pr_sx_date"][i-1]


    # percentage deaths
    #odata["dth_pc_after_exact_age"][1:clen-1] = [ (odata["death_percent"][i] - odata["death_percent"][i+1])  for i in  np.arange(1,clen-1, 1)]
    for i in np.arange(1,clen-1,1):
        odata["dth_pc_after_exact_age"][i] = odata["death_percent"][i] - odata["death_percent"][i+1]

    odata["dth_pc_after_exact_age"][clen-1] = odata["death_percent"][clen-1]
    #print(odata)

    # proportion of people who will die before iage
    beforeDod = odata["dth_pc_after_exact_age"][1] * (iage - flr_age)/5
    odata["dth_pc_after_exact_age"][1] = odata["dth_pc_after_exact_age"][1] - beforeDod
    odata["dth_pc_after_exact_age"] = odata["dth_pc_after_exact_age"]* 100/odata["dth_pc_after_exact_age"].sum()


    # add 5 to each of the "ages"
    if iage>=5:
        odata["lower_age"] = odata["lower_age"]+5
    else:
        odata["lower_age"] = odata["lower_age"]+iage

    output = odata.ix[1:clen-1,['lower_age', 'dth_pc_after_exact_age']]
    return output
# --- function end --- #

# data input
cntry = "Nepal"
sex = 1 #1=Man, 2=Woman
idate = time.strftime('%Y-%m-%d')
iage =0

#print(cntry, sex, idate, iage)
output = dist_odata(cntry, sex, idate, iage)
print output

#plt.plot(output['lower_age'], output['dth_pc_after_exact_age'])
# plt.show()

# spl = InterpolatedUnivariateSpline(output['lower_age'], output['dth_pc_after_exact_age'])
# yrs = np.arange(output['lower_age'][0],output['lower_age'][len(output)-1])
# plt.plot(yrs,abs(spl(yrs)))

# --- part 2 --- #
# find percentiles
#f = InterpolatedUnivariateSpline(output['lower_age'], output['dth_pc_after_exact_age'].cumsum())
#print f.get_coeffs()




'''
# time for list comprehension!
f = np.array([interpolate.interp1d(dates, odata.ix[i,1:4])(daysSinceEpoch(idate)) for i in np.arange(0, len(cohort.columns),1)])
print f

# test interpolation
test = np.arange(1, 4, 1)
f = interpolate.interp1d(dates, test)
print f(daysSinceEpoch(idate))

f= []
for i in np.arange(1,len(odata["death_percent"]),1):
    f.append((odata["death_percent"][i]-1)*(odata["pr_sx_date"][i]-1))
print f[::-1]


'''