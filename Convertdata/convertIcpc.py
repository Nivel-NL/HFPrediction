# Functions to
# 1. (convertICPCdata) save the non-target episode or chronic icpc codes, and only the target-icpc from chronic 
from .utilDef import convertCodeToICPC, str2date
from .io_data import dictlistToCSV, import_data

def convertICPCdata(rows, headers, ICPCcodeToSelect, isICPC, savefile, in_dir):
    # Converts episode or chronic icpc codes.
    # If it is the episode file with icpc, it removes the ICPC code corresponding to the disease.
    # If it is the chronic file with icpc, it only select the ICPC code corresponding to the disease.
    # If it is the chronic file without icpc, it removes the icpc code corresponding to the disease
    
    # Initialize the indexes of the headers
    # The headers differ for the chronic file (first) and the icpc file (second)
    ID_idx = headers.index('randompatnr')
    if isICPC == False or ICPCcodeToSelect == 'Chronic':
        icpc_idx = headers.index('episodeicpc')
        begin_idx = headers.index('startdatum')
    else:
        icpc_idx = headers.index('icpc')
        begin_idx = headers.index('datum')
    
    # Set what the headers of the file to create will be
    convertedDataHeader=['gp_patidf', 'gp_epssince', 'gp_epsicpc']
    
    # Initialize list
    convertedData = []
    count=0
    
    # Select episode codes which are valid (chronic)
    if isICPC == False or ICPCcodeToSelect == 'Chronic':
        # Select the ICPC file
        rows_chronicFile, fields_chronicFile = import_data(in_dir + '\\ICPC_chronisch_uitleg.csv', delim = ';')
        icpc_cidx = fields_chronicFile.index('icpc')
        duration_cidx = fields_chronicFile.index('categorie')
        icpc_chronicCodes = []
        
        # Select the rows where the file describes the ICPC code as "Chronic"
        for row in rows_chronicFile:
            if (row[duration_cidx]=='Chronisch') or (row[duration_cidx]=='Langdurig_1j'):
                icpc_chronicCodes.append(row[icpc_cidx])
                
    else:
        # This is used for normal ICPC codes; uses all codess
        icpc_chronicCodes = False
    
    # Each row represent a single icpc code for a single patient. 
    # The code is saved in the convertedData file.
    # Depending on the file and the icpc (see function), it selects codes
    for row in rows:
        
        # Select the ID, ICPC code (as letter+number) and date (right format)
        key = int(row[ID_idx])
        ID_icpc = convertCodeToICPC(row[icpc_idx])
        ID_date = str2date(row[begin_idx],ymd=False)
        
        # Only includes the chronic codes or all codes for icpc
        if (icpc_chronicCodes !=False) and (ID_icpc[0:3] not in icpc_chronicCodes):
            continue
        
        # ICPC codes between 30 and 70 are removed (are things as flu shots)
        if (int(ID_icpc[1:3])>=30) and (int(ID_icpc[1:3])<70):
            continue
        
        # Three options are possible: 
        # 1. ICPC data: all rows are included, except the rows with the ICPC code to find
        # 2. no ICPC data: only the ICPC codes are selected from the chronic data and appended
        # 3. Chronic data: all chronic diseases except the icpc code to find are saved (in a seperate file) 
        
        if isICPC is False:
            # Option 2: Only select and savethe icpc code to find
            if ID_icpc == ICPCcodeToSelect:
                convertedData.append({'gp_patidf': key, 'gp_epssince':ID_date, 'gp_epsicpc': ID_icpc})
                count = count+1
                
                # Saving in between for memory error
                if count == 50000:
                    dictlistToCSV(convertedData, convertedDataHeader, savefile)
                    convertedData = []
                    count=0
        
        else:
            # Option 1 + Option 3 (depends on wheter chronic or icpc data is loaded)
            # Select all icpc codes except the icpc code to find
            if ID_icpc != ICPCcodeToSelect:
                convertedData.append({'gp_patidf': key, 'gp_epssince':ID_date, 'gp_epsicpc': ID_icpc})
                count = count+1
                
                # Saving in between for memory error
                if count == 50000:
                    dictlistToCSV(convertedData, convertedDataHeader, savefile)
                    convertedData = []
                    count=0  
                    
    # Saving the rest of the data at the end
    if count != 0:
        dictlistToCSV(convertedData, convertedDataHeader, savefile)