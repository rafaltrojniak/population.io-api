
#setwd("/Users/apple/Desktop/dodpy/workspace/") #set working directory#KC#
setwd("C:/Users/tkriszti/Dropbox/rank and cohort life expectancy/date of death/dodpy/workspace")
library("splines")

sx_ages <- read.csv("Survival_ratio_Cohort_ages.csv")#


# ------------------------------- dist_sx function --------------------------- #
dist_sx <- function (CNTRY1,iSEX1,sx_date,sx_exact_age) {#KC#
  #find beginning of 5 yearly period for the sx_date
  sx_yr <- as.numeric(substr(sx_date,1,4))
  lowest_yr <- floor(sx_yr/5)*5 #lower limit of the five yearly period that includes sx_yr 
  
  lowest_age <- floor(sx_exact_age/5)*5
  selages <- match(paste("X",lowest_age-5,sep=""),names(sx_ages)):match("X125",names(sx_ages))#starting one step earlier
  
  #the diagonal is the cohort we are interested
  sx_mat  <- subset(sx_ages,region==CNTRY1 & sex==iSEX1 & Begin_prd >=(lowest_yr-5),select=selages) #extract a row corresponding to the time-period#KC#
  #select older cohort (for interpolation purpose)
  sx_mat_older  <- subset(sx_ages,region==CNTRY1 & sex==iSEX1 & Begin_prd >=(lowest_yr-10),select=c(selages)) #extract a row corresponding to the time-period#KC#
  #select younger cohort (for interpolation purpose)
  sx_mat_younger  <- subset(sx_ages,region==CNTRY1 & sex==iSEX1 & Begin_prd >=(lowest_yr),select=c(selages)) #extract a row corresponding to the time-period#KC#
  
  #dates for interpolation corresponding to the three periods 
  dates_x<- as.numeric(as.Date(c(paste(lowest_yr-5+3,1,1,sep="/"),paste(lowest_yr+3,1,1,sep="/"),paste(lowest_yr+5+3,1,1,sep="/")),"%Y/%m/%d"))
  #set place holder for calculation
  sx <- matrix(0,length(selages),7)
  colnames(sx) <- c("lower_age","pr0","pr1","pr2","pr_sx_date","death_percent","dth_pc_after_exact_age")
  #fill the first column with age (starting age of each five yearly age groups)
  sx[,1] <- seq((lowest_age-5),125,by=5)
  
  for ( i in 1:length(selages)) { #27 Sx values.. newborn, 0-4, ...., 125-129
    #fill the values
    sx[i,2] <- sx_mat_older[i,i]     
    sx[i,3] <- sx_mat[i,i]     
    sx[i,4] <- sx_mat_younger[i,i]     
    #interpolated to get SX for the sx_date
    sx[i,5] <- spline(sx[i,2:4]~dates_x,xout=as.numeric(sx_date))$y #   #interpSpline does not work with three values.. so used spline function here which also fits linearly
  } 
  
  #Calculate the % deaths starting at the lower age of the age-group where the sx_exact_age lies
  sx[1,6] <- 0
  sx[2,6] <- 100 #this is the starting population 
  for (i in 3:length(selages)) {
    sx[i,6] <- sx[i-1,6]*sx[i-1,5]
  } 
  
  #col7: % deaths
  for (i in 2:(length(selages)-1)) {
    sx[i,7] <- sx[i,6] - sx[i+1,6] 
  } 
  sx[i+1,7] <- sx[i+1,6] #everyone dies in this age-group
  
  #proportion of people who will die before the sx_exact_age
  die_earlier <- sx[2,7]*(sx_exact_age - lowest_age)/5
  sx[2,7] <-sx[2,7] - die_earlier #this is the proportion who died in this age-group after the sx_exact_age
  sx[,7] <- sx[,7] * 100/sum(sx[,7])
  sx[,1]<-sx[,1]+5
  
  sx[-1,c(1,7)]
} # function end

#Example a person who is aged 34.3 years on 2020-01-01
#this gives distribution of deaths (in percentage) of those 34.3 years old on 2020-01-01
#SX_DATE <- "2020-01-01"
SX_DATE <- Sys.Date()

SX_AGE <- 40 
deathsbyage <- dist_sx(CNTRY1="Nepal",iSEX1 = 1,sx_date=as.Date(SX_DATE),sx_exact_age=SX_AGE)
#this is the distribution of deaths by age
plot(deathsbyage,ylab = "Percent dying before Age", xlab="Age", type="b")

#finding percentiles
ispl <- interpSpline(cumsum(deathsbyage[,2])~deathsbyage[,1],bSpline = TRUE)
ispl
#function to calculate percentile
cal_percentile <- function (ispl=ispl,agex,perc) {
  (predict(ispl,agex)$y - perc)^2
}

#plotting...
plot(ispl, ylab = "Cumulative Percent dying before Age", xlab="Age")


#Median (e.g.)
PERC = 50
PERCAGE <- optimize(f=cal_percentile,interval = c(0:130),ispl=ispl,perc=PERC)$minimum
paste(PERC," percent of the population aged", SX_AGE, "years old who are alive on", SX_DATE,"will die before age",round(PERCAGE,1),"years",sep=" ")
points(x=PERCAGE,y=PERC)
lines(x=c(PERCAGE,PERCAGE),y=c(0,PERC))
lines(x=c(0,PERCAGE),y=c(PERC,PERC))
text(x=PERCAGE,y=0,paste("Median Age",round(PERCAGE,1),"yrs",sep=" "))


#First Quartile (25th percentile)
PERC = 25
PERCAGE <- optimize(f=cal_percentile,interval = c(0:130),ispl=ispl,perc=PERC)$minimum
paste(PERC," percent of the population aged", SX_AGE, "years old who are alive on", SX_DATE,"will die before age",round(PERCAGE,1),"years",sep=" ")
points(x=PERCAGE,y=PERC)

#####plotting declining percentage of live people#####

#finding percentiles

nrow(deathsbyage)  
alivebyage <- (cumsum(deathsbyage[nrow(deathsbyage):1,2]))[nrow(deathsbyage):1]
aliveage <- c(SX_AGE,deathsbyage[-(nrow(deathsbyage)),1])

#fitting spline 
ispl_live <- interpSpline(alivebyage~aliveage,bSpline = TRUE)

#plot
plot(ispl_live, ylab = "Cumulative Percent alive by Age", xlab="Age")


#Median (e.g.)
PERC = 50
PERCAGE <- optimize(f=cal_percentile,interval = c(0:130),ispl=ispl_live,perc=PERC)$minimum
paste(PERC," percent of the population aged", SX_AGE, "years old who are alive on", SX_DATE,"will die before age",round(PERCAGE,1),"years",sep=" ")
points(x=PERCAGE,y=PERC)
lines(x=c(PERCAGE,PERCAGE),y=c(0,PERC))
lines(x=c(0,PERCAGE),y=c(PERC,PERC))
text(x=PERCAGE,y=0,paste("Median Age",round(PERCAGE,1),"yrs",sep=" "))



