# Function to
# 1. (convertICPCCounts) save a dictionary with per patient unique dates of icpc codes (which later can be counted)
import pickle
from .utilDef import str2date
    
def convertICPCCounts(rows, headers, out_dir):
    # Save a dictionary with per patient unique dates of icpc codes (which later can be counted)
    
    # Initialize the indexes of the headers
    ID_idx = headers.index('gp_patidf')
    date_idx = headers.index('gp_epssince')

    # Initialize empty dict
    convertedData = {}
    
    # Each row is an ICPC code
    # Use each row to count the total number of unique days for icpc codes
    for row in rows:
        
        # Get patient ID and data (right format)
        key = int(row[ID_idx])
        datum = str2date(row[date_idx], ymd=True)
        
        # Save unique dates of ICPC visits per patient (as key in the dict)
        if key in convertedData:
            if datum not in convertedData[key]:
                convertedData[key].append(datum)
        else:
            convertedData[key] = [datum]
    
    # Sort the unique dates per patient for later preprocessing
    for rij, waarde in convertedData.items():
        waarde.sort()
        
    # Save the date per patient per icpc codes
    f= open(out_dir + '\\gp_journaldata', 'wb')
    pickle.dump(convertedData, f)
    f.close()
    
