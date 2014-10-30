Methodology
===========

_Population.io_ uses official demographic data produced by the United Nations and published in the World Population Prospects (see data sources for details) most of which is available in annual or 5-year cycles. _Population.io_ uses the past estimates for 1950-2010 and the medium population projection up to 2100 and interpolates the distribution daily for the World and for 200 countries (excluding few countries with small population size) and uses the UN’s estimates and projections of life tables for interpolating individual life expectancy by date and place of birth. Specifically, the following interpolation techniques were used:

- Annual population by age in single year and sex in 1st July of each year was interpolated to single day by fitting spline function. The daily population by age in single year and sex were interpolated for ages in days by fitting spline function.
- Remaining life expectancy at specific age (in days) was obtained by interpolating (spline) the 5 yearly/duration age-specific period life expectancies.

### Data sources

- [World Population Prospects (2012 Revision)](http://esa.un.org/wpp/), United Nations Population Division (released in 2013)

- ["WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.csv"](https://github.com/worldpopulation/population.io-api/blob/master/data/WPP2012_INT_F3_Population_By_Sex_Annual_Single_100_Medium.zip): Annual population distribution by single age and sex: for the period 1950-2010 (estimates) and 2011-2100 (Medium projection) for 200 countries with population size greater than 90,000 (in 2013) as well as for several UN World regions.

- Age specific period life expectancy by sex – 5 yearly interval for age and duration – for the period 1950-2010 (estimates) and 2010-2100 (projections). Data were extracted from a file obtained from the UN.

