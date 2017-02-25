#!/home/mplace/anaconda3/bin/python
"""
Program: tecanMean.py 

Purpose: Calculate average growth rate across technical replicates in a tecan file.

Input  : Tecan file (export as tab delimited file from excel) and Well Contents file

        Tecan file is a text file with an extensive header and multiple
        tables each of which starts with a line Cycles / Well, the next line
        is the well location  A1  (true start of the table) and has many columns.
        The mean row is read in for analysis.       
        
        Well Contents file provides replicate information:
        
        Well	Strain	Condition
        B2	Hog1-GFP, Pbs2Δ, S83	Acetate_noWash

        
Output: A text version of the tecan with the well name (like B2) replaced by the
        strain name and a text table file with the seconds converted to minutes
        and well average.
        
        table with the following columns:
        Time(hours)  0     60    120
        samples      OD readings
        
Steps:
    The Tecan file is read line by line and each table is processed when it is 
    located.
    
@author : Mike Place
@date   : 02/17/2017
@version: 1.0
"""
import argparse 
from collections import defaultdict
import csv
import itertools
import os
import sys
import re
import unicodecsv                  #
import xlrd                        # handle excel files


def readTecanFile(inFile):
    """
    Read in  Tecan file, expected to be a tab delimited text file.
    Only return rows of interest: sample, Time, Mean
    """
    with open(inFile, 'r') as inf:
        for _ in range(55):                          # skip header information
            next(inf)
        for line in itertools.islice(inf,5):         # this gets the first well
            yield line
        while True:
            # We need to know the number of samples per time point
            #lines = list(itertools.islice(inf,18,23))
            lines = list(itertools.islice(inf,7,12))
            for line in lines:
                yield line
            if not lines:
                break
            
def toExcel( file ):
    """
    Converts an Excel file to a CSV file.
    If the excel file has multiple worksheets, only the first worksheet is converted.
    Uses unicodecsv, so it will handle Unicode characters.
    Uses a recent version of xlrd, so it should handle old .xls and new .xlsx equally well.
    """        
    wb = xlrd.open_workbook(file)
    sh = wb.sheet_by_index(0)

    name = re.sub('.xlsx', '.txt', file)
    fh = open(name,"wb")
    csv_out = unicodecsv.writer(fh, delimiter='\t', encoding='utf-8')

    for row_number in range (sh.nrows):
        csv_out.writerow(sh.row_values(row_number))

    fh.close()
    return name
    
def main():
    cmdparser = argparse.ArgumentParser(description="Calculate Mean Growth Rate for technical replicates in a Tecan file.",
                                        usage='%(prog)s -f <tecan file> -s <sample info file>' ,prog='tecanGrowthRate.py'  )
    cmdparser.add_argument('-f', '--file', action='store',     dest='FILE', help='Tecan File, excel file.')
    cmdparser.add_argument('-s', '--sample', action='store',   dest='SAMPLE', help='Sample Information file.')        
    cmdparser.add_argument('-i', '--info', action='store_true', dest='INFO', help='Detailed help informations')
    cmdResults = vars(cmdparser.parse_args())
    
    if len(sys.argv) == 1:
        print("")
        cmdparser.print_help()
        sys.exit(1)      
    
    if cmdResults['INFO']:
        print("\n tecanMean.py")
        print("\n Purpose: Calculate Average Growth Rate for technical replicates in a Tecan file.")
        print("\n Input : Tecan text file & a sample info file.")
        print("          ." )
        print(" Required Parameters: -f tecan.xlsx -s sample-Info.xlsx")
        print("  sample-Info.xlsx has 3 columns:")
        print("\tWell    Strain	                Condition")
        print("\tB2	Hog1-GFP,Pbs2Δ,S83	Acetate_noWash")
        print()
        print(" To run:  /home/GLBRCORG/mplace/scripts/tecanMean.py -f tecan.xlsx -s sample-Info.xlsx\n")
        print(" Output: Text table \n")     
        print("\tSee Mike Place for help.")
        print("")
        print(sys.exit(1)) 
        
    if cmdResults['FILE']:
        infile = cmdResults['FILE']       
        tecanFile = toExcel(infile)
        if not os.path.exists(tecanFile):
            print()
            print("\ntecan file does not exist")
    else:
        print("")
        cmdparser.print_help()
        sys.exit(1)
    
    if cmdResults['SAMPLE']:
        infile = cmdResults['SAMPLE']
        sampleFile = toExcel(infile)
    else:
        print()
        cmdparser.print_help()
        sys.exit(1)
        
    # create a dictionary for sample Information
    # example: defaultdict(<class 'dict'>, {'C2': {'condition': 'Acetate_noWash', 'name': 'Hog1-GFP-Pbs2Δ-S83Arep2'}
    smpInfo = defaultdict(dict)
    findTime = False
    # read sample information file, note the initial strain info looked like: "Hog1-GFP, Pbs2Δ, S83", I removed the comma and spaces   
    with open(sampleFile, 'r') as sf:
        for sample in sf:
            sample = sample.rstrip()
            if sample.startswith('Well'):        # skip the header
                continue
            else:
                tmp = sample.split('\t')
                fixFormat = tmp[1].split(', ')
                tmp[1] = '-'.join(fixFormat)
                smpInfo[tmp[0]] = { 'name': tmp[1], 'condition':tmp[2]} # load the dictionary
    
    # rename wells and write a new tecan text file
    newTecan = open('new-tecan.txt', 'w')
    with open(tecanFile, 'r') as f:
        for row in f:
            row = row.rstrip()
            if re.search(r'^[A-Z]{1}\d{1,2}', row):
                newRow = row.split('\t')
                newRow[0] = smpInfo[newRow[0]]['name']+'-'+smpInfo[newRow[0]]['condition']
                newTecan.write('\t'.join(newRow))
                newTecan.write('\n')
            else:
                newTecan.write('%s\n' % row)  
    newTecan.close()
    # create dictionary for mean information
    meanData = defaultdict(list)
    
    with open(tecanFile, 'r') as inf:
        for _ in range(54):                          # skip header information
            next(inf)
        for row in inf:
            row = row.rstrip()
            if row.startswith('Cycles'):
                if not findTime:                     # first sample
                    sample = inf.readline().rstrip().split('\t')    # get sample name row (example:  "B2    1    2    3")
                    timeline = inf.readline().rstrip()              # get times, only need this once
                    times = timeline.split('\t')
                    times.pop(0)                                    # remove the Times [s] , first index
                    times = [ str(int(float(x)/60)) for x in times ]# convert to seconds
                    times.insert(0, 'Time [m]')               
                    findTime = True
                    inf.readline()                   # skip Temp.[C] row
                    sampleMean = inf.readline().rstrip().split('\t')# get mean data row
                    sampleMean.pop(0)
                    #print('\t'.join(times))
                    #print(sample)                    
                    #print(sampleMean)
                    #print(smpInfo[sample[0]]['name'])
                    meanData[smpInfo[sample[0]]['name']+'-'+smpInfo[sample[0]]['condition']].append(sampleMean)
                    continue
                else:
                    sample = inf.readline().rstrip().split('\t') 
                    inf.readline()   # skip Time[s] row
                    inf.readline()   # skip Temp.[C] row
                    sampleMean = inf.readline().rstrip().split('\t') 
                    sampleMean.pop(0)
                    meanData[smpInfo[sample[0]]['name']+'-'+smpInfo[sample[0]]['condition']].append(sampleMean)
                    #print(smpInfo[sample[0]]['name'])
                    #print(sample)
                    #print(sampleMean)        
    total = 0
    avg   = 0
    print('\t'.join(times))
    for ky, v in meanData.items():
        print(ky,end='\t')
        for j in range(len(v[0])):
            for i in range(len(v)):
                #print(j,i, float(v[i][j]), end = '\t')
                total += float(v[i][j])
            #print("total %s" % total , end = '\t')
            avg = total/len(v)
            print('%s' % avg, end = '\t')
            total = 0
        print()
                #print(avg)
            
        
                 
    #print(meanData['Hog1-GFP-Pbs2Δ-S83'][0])
    #print()
    #print(meanData['Hog1-GFP-Pbs2Δ-S83'][1])    
    
        
                
if __name__ == "__main__":
    main()

####################################################################################################
