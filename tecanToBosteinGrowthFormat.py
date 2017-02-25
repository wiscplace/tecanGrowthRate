#!/home/mplace/anaconda3/bin/python
"""
@Program: tecanToBosteinGrowthFormat.py

@Purpose: Read Tecan file output table with format as follows:
    
    well name    0      15    30   45
    A1   sample1 0.001  .052  .102  .155
    ....
          
@Input:   Tecan file exported as tab delimited text file
                            
@Output: csv table


@author: Mike Place
@Date:   2/6/2017
"""
import re
import sys

    
def main():
    """
    Main 
    """
    if len(sys.argv) < 1:
        print("\n\tInput file required.")
        print("\ttecanToBosteinGrowthFormat.py tecanTabFile.txt ")
        print("\n")
        sys.exit(1)
    else:
         tecanFile   = sys.argv[1]  # tecan tab file file  
    
    time = []
    time.append('Well')
    time.append('Name')  
    for n in range(0,1560,20):   # this sets up the time 0 to 25.6 hours every 20 minutes
        time.append(str(n))
    
    print(','.join(time))
    
    with open(tecanFile, 'r') as tf:
        sample = ''
        for line in tf:
            if re.match("^[A-G]+\d+", line):
                d = line.split()
                sample = d[0]
            elif re.match("^Mean", line):
                line = line.rstrip()
                d = line.split()
                d[0] = sample + '-' + d[0]
                mean = ','.join(d)
                print('%s,%s' %(sample, mean) )
            
if __name__ == "__main__":
    main()
    




