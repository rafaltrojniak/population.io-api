Data and Method
===============

What are the data sources?

World Population Prospects (2012 Revision), United Nations Population Division (released in 2013)

1. ["WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.csv"](https://github.com/worldpopulation/population.io-api/blob/master/data/WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.zip): Annual population distribution by single age and sex:
  for the period 1950-2010 (estimates) and 2011-2100 (Medium projection) for 196 countries with population size greater 
  than 100,000 (in 2010) as well as for several UN World regions. 

2. Age specific period life expectancy by sex - 5 yearly interval for age and duration - 
   for the period 1950-2010 (estimates) and 2010-2100 (projections).
   Data were extracted from a file obtained from the UN on request. 


Interpolation 

1. Annual population by age in single year and sex in 1st July of each year were first interpolated to single day by fitting spline function. 
   For e.g. interpolated between 1 year old in 1st July 2010 and 1 year old in 1st July 2011 to get 1 year olds in 2nd July 2010 to 30th June 2011
 
2. The daily population by age in single year and sex were interpolated for ages in days by fitting spline function.
   For e.g. Interpolated between 1 year old and 2 years old, assigning the 1 year old to 365+183 days of exact age
   and 2 years old to 364*2 + 183 days and so on.

3. Remaining life expectancy at specific age (in days) were obtained by interpolating (spline) the 5 yearly/duration age-specific period life expetancies.

