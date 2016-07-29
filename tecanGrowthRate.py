#!/home/GLBRCORG/mplace/anaconda3/bin/python
"""
Program: tecanGrowthRate.py 

Purpose: Calculate Growth Rate for all samples in a Tecan file.

Input  : Tecan file (export as tab delimited file from excel)

        Tecan file is a text file with an extensive header and multiple
        tables each of which starts with a line Cycles / Well, the next line
        is the well location  A1  (true start of the table) and has many columns.
        The mean row is read in for analysis.       
        
Output: A text file, table with the following columns:
        SampleName  X R^2  GrowthRate
        
Steps:
    The Tecan file is read line by line and each table is processed when it is 
    located.
    
    The mean values > .25 and < .75 are used to fit an exponential curve and 
    R squared is calculated.  Then equation Y = e^(kx) is solved for x and used
    to calculate growth rate:  ln(2)/x 

Dependencies: R must be in path

@author : Mike Place
@date   : 06/8/2016
@version: 1.0
"""
import argparse 
from collections import OrderedDict
import csv
import itertools
import os
import sys
import re
import subprocess 

#stats = importr('stats')
#base  = importr('base')

def readTecanFile(inFile):
    """
    Read in  Tecan file, expected to be a tab delimited text file.
    Only return rows of interest: sample, Time, Mean
    """
    with open(inFile, 'r') as inf:
        for _ in range(55):                          # skip header information
            next(inf)
        for line in itertools.islice(inf,5):
            yield line
        while True:
            lines = list(itertools.islice(inf,18,23))
            for line in lines:
                yield line
            if not lines:
                break
    
def main():
    cmdparser = argparse.ArgumentParser(description="Calculate Growth Rate for all samples in a Tecan file.",
                                        usage='%(prog)s <tecan file>' ,prog='tecanGrowthRate.py'  )
    cmdparser.add_argument('-f', '--file', action='store',     dest='FILE', help='Tecan File, converted to tab delimited text.')        
    cmdparser.add_argument('-i', '--info', action='store_true', dest='INFO', help='Detailed help informations')
    cmdResults = vars(cmdparser.parse_args())
    
    data = OrderedDict() 
    tmpFiles = []
    
    if len(sys.argv) == 1:
        print("")
        cmdparser.print_help()
        sys.exit(1)      
    
    if cmdResults['INFO']:
        print("\n tecanGrowthRate.py")
        print("\n Purpose: Calculate Growth Rate for all samples in a Tecan file.")
        print("\n Input : Tecan text file. Generate text file by exporting the tecan excel")
        print("          sheet as a plain tab delimited text file." )
        print(" Required Parameters: -f tecan.txt")
        print(" Rscript exponential_Fit.R must be in current directory")
        print(" To run:  /home/GLBRCORG/mplace/scripts/tecanGrowthRate.py -f tecan.txt\n")
        print(" Output: Text table \n")     
        print("\tSee Mike Place for help.")
        print("")
        print(sys.exit(1))     
    
    if cmdResults['FILE']:
        infile = cmdResults['FILE']       
        if os.path.exists(infile):
            tri = 0
            for line in readTecanFile(infile):
                line = line.rstrip()
                if line.startswith('Time'):
                    Time = line.split()
                    Time.remove('[s]')
                    tri += 1
                elif line.startswith('Mean'):
                    Mean = line.split()
                    tri += 1
                elif re.match("^[A-G]+\d+", line):
                    Sample = line.split()
                    tri += 1
                
                if tri ==3:
                    tri = 0
                    SampleName = Sample[0] + '.csv'
                    tmpFiles.append(SampleName)
                    with open( SampleName, 'w') as outF:
                        writer = csv.writer(outF, delimiter='\t')
                        writer.writerows(zip(Mean,Time))
            # loop through tmpFiles to call R script to calculate exponential fit
            for file in tmpFiles:
                cmd = [ 'Rscript','exponential_fit.R', file ]   
                #cmd = [ 'Rscript','/home/mplace/projects/tecanGrowthRate/exponential_fit.R', file ]               
                output  = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                result  = output[0].decode( 'utf-8' )
                name = re.sub(r'.csv', '', file)
                #result1 = output[1].decode( 'utf-8' )
                data[name] = []
                row = result.split('\n')
                for rx in row:
                    rx = rx.rstrip()
                    if rx.startswith('NO DATA'):
                        data[name].append("NO DATA")   
                    if rx.startswith('R^2'):
                        value = rx.split(':')
                        data[name].append(value[1])
                    if rx.startswith('Growth'):
                        value = rx.split(':')
                        data[name].append(value[1])

    # write to file                        
    with open("tecan-result.txt", 'w') as out:
        out.write("Cell_ID\tR^2\tGrowthRate\n")
        for k,v in data.items():
            k = k + '\t'
            out.write(k)
            out.write('\t'.join(v))
            out.write('\n')                    
                    
if __name__ == "__main__":
    main()

####################################################################################################
"""
Here is the Rscript file, if you don't have one.
Copy this to a text file and name it exponential_fit.R 

THE FOLLOWING LINE:   cmd = [ 'Rscript','/home/mplace/projects/tecanGrowthRate/exponential_fit.R', file ]   
MIGHT NEED TO BE CHANGED TO REFLECT THE SCRIPT PATH, or just place the file in the current 
working directory.

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


"""
