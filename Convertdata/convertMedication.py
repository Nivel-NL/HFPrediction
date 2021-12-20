# Function to
# 1. (convertMedicationData) convert medication csv file to a standard format
from os import path
from .io_data import dictlistToCSV, write_csv
from .utilDef import str2date
    
def convertMedicationData(rows, headers, savefile):
    # Convert raw medication csv file to a standard format   

    # Initialize the indexes of the headers 
    ID_idx = headers.index('randompatnr')
    atc_idx = headers.index('atc')
    date_idx = headers.index('datum')
    
    # Set what the headers of the file to create will be
    convertedDataHeader=['gp_patidf', 'gp_medprd', 'gp_medatc']
    
    # Initialize empty lists
    convertedData = []
    count=0
    
    # Each row represent a single atc code for a single patient.
    # The rights columns are loaded, converted in the right format and exported
    for row in rows:
        
        # Get ID of patient
        key = int(row[ID_idx])
        
        # Set the length of a ATC code at a length of 5. Smaller lengths are not taken into account
        if len(row[atc_idx])>=5:
            ID_atc = row[atc_idx][0:5]
        else:
            continue
        
        # Convert the date into the right format (is not uniform in raw file)
        ID_date = str2date(row[date_idx],ymd=False)
        
        # Append the right rows to convertedData in a dict-in-list format
        # This format is used for saving
        convertedData.append({'gp_patidf': key, 'gp_medprd':ID_date, 'gp_medatc': ID_atc})  
        count = count+1
        
        # The count section is used to iteratively save parts of the medication file.
        # Otherwise, an memory error may occur.
        if count == 50000:
            dictlistToCSV(convertedData, convertedDataHeader, savefile)
            convertedData = []
            count=0
    
    # At the end, save also the remaining atc codes
    if count != 0:
        dictlistToCSV(convertedData, convertedDataHeader, savefile)
