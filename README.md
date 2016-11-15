********************************************************************************
tecanGrowthRate.py

    Purpose: Calculate Growth Rate for all samples in a Tecan file.

    Input : Tecan text file. Generate text file by exporting the tecan excel
            sheet as a plain tab delimited text file.
    
    Required Parameters: -f tecan.txt
    
    Rscript exponential_Fit.R must be in directory you are working in.
        
        to copy the file: cp /home/GLBRCORG/mplace/scripts/tecanGrowthRate/exponential_fit.R yourDirectory
    
    To run:  /home/GLBRCORG/mplace/scripts/tecanGrowthRate -f tecan.txt

    Output: Text table 

    version 1.0 July 2016 
*********************************************************************************
exponential_fit.R

    Purpose: R script to calculate exponential growth rate, called from Python

    Input  : Data passed in is a single sample file w/ 2 columns Mean, Time

    Output : R^2 and Growth Rate are calculated and returned
 
    version 1.0 July 2016
*********************************************************************************
NOTES for Mac users:

    MS Excel on Mac does not export a tab delimited file in a format this 
    script can use.  Instead use LibreOffice or OpenOffice calc and export 
    a file which is tab delimited without quotes using utf-8 for encoding.  

*********************************************************************************


