# exponential_fit.R
# Author : Mike Place
# Date   : 7/26/2016
# Purpose: R script to calculate exponential growth rate, called from Python
# Input  : Data passed in is a single sample file w/ 2 columns
#          Mean, Time
# Output : R^2 and Growth Rate are calculated and returned
# 
# #############################################################################
#import 
library(stats)
# check command line arguments
args = commandArgs(trailingOnly = TRUE)
if(length(args)==0){
  stop("Missing input file for Rscript!.n", call.=FALSE)
}else if (length(args)==1){
  indata = args[1]
}
# load data
e <- read.csv(indata, header=TRUE, sep = '\t')
#plot(e$Time, e$Mean)

# Select the data range Dee specified this range as being the exponential segment of the data.
ef <- subset(e, Mean >= .25 & Mean <= .70)
if( nrow(ef) != 0) {
m <- nls( ef$Mean ~ (a * exp(b * ef$Time)), data = ef, start = list(a=1, b = 0), trace = T)

# plot and fit line
#plot(ef$Time,ef$Mean, pch=19)
#lines(ef$Time, predict(m, list(ef$Time)), col = "blue")

# residual sum of squares
RSS.p <- sum(residuals(m)^2)
# Total sum of squares
TSS <- sum((ef$Mean - mean(ef$Mean))^2)
# R-squared 
r2 <- 1 - (RSS.p/TSS)

# growth rate
values <- m$m$getPars()[2]
GrowthRate <- (log(2)/values)/60

cat(paste0("R^2:", r2))
cat(paste0("\n"))
cat(paste0("Growth Rate:", GrowthRate))
} else{
  cat(paste0("NO DATA"))
}
# END OF FILE