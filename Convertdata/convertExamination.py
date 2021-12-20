# Functions to
# 1. (getContentList) return an ordened list containing all possible examination codes and corresponding types.
# 2. (alterValue) from a string value, remove spaces and ranges and return a float value
# 3. (convertData_nhg) return examination data converted to a single format with a value depending on the type.
# 4. (convertFalseData) converts not well processed data (such as due to free text) to well processed data
# 5. (combineCorrectedData) calls a correcting function for falseData and combines the correct and corrected data.
# 6. (findFilesInDir) return the files in the selected directory starting with the string
# 7. (processUitslagenFiles) Main call file to process raw examination files to a standard format. 
from .utilDef import str2date
import os
from .io_data import dictlistToCSV, write_csv, import_data

def getContentList(in_dir):
    # Read the file containing all possible examination codes and corresponding types.
    # Return an ordened list of these codes
    
    # Open and read the file
    file = open(in_dir + '\\NHG-Tabel 45 Diagnostische bepalingen - versie 34 - bepaling.txt','r')
    content = file.read()
    
    # Order the text based on rows and tabs
    content_list_temp = content.split('\n')
    del content_list_temp[0]
    
    # Get the right header and remove the header
    header = content_list_temp[0].split('\t')
    del content_list_temp[0]
                                 
    content_list={}
    
    # A single row is one examination code with tabs. Split based on tabs and save info in a dict based on code nr
    for row in content_list_temp:

        content_list[int(row.split('\t')[0])] = row.split('\t')

    return content_list

def alterValue(value):
    # From a string value, remove spaces and ranges and return a float value
    
    # Remove spaces
    value = ''.join([x for x in value if x !=' '])
    
    # If < or > exist in the value, save the value as value - 1%.
    # This ensures a float instead of a range.
    # If both < and > are in the value, it cant be processed
    # In addition, replace , (dutch) by .
    if '<' in value and '>' in value:
        return float(value) #Raises error
    elif '<' in value:
        value = ''.join([x for x in value if x.isdigit() or x in [',','.']])
        value = float(value.replace(',','.'))
        value = value - (value/100) # Makes a float
    elif '>' in value:
        value = ''.join([x for x in value if x.isdigit() or x in [',','.']])
        value = float(value.replace(',','.'))
        value = value + (value/100) # Makes a float
    else: 
        value = float(value.replace(',','.'))
            
    return value

def convertData_nhg(rows, headers, in_dir, out_dir):
    # Return examination data converted to a single format with a value depending on the type.
    # Checks if the data is processed correctly, otherwise returns in falseData.
    
    # Initialize the indexes of the headers
    ID_idx = headers.index('randompatnr')
    nhg_idx = headers.index('nhgnummer')
    begin_idx = headers.index('datum')
    waarde_idx = headers.index('waarde2')
    
    # Set what the headers of the file to create will be
    convertedDataHeader=['gp_patidf', 'gp_exadate', 'gp_exacod','gp_waarde']
    
    # Initialize empty dicts and lists
    convertedData = []
    falseData = dict()
    wrongData=[]
    VTDTMKdata=[]
    emptyData = []
    falseDataCount=0
    
    # Initialize a list consisting of all known examination codes and types
    contentlist = getContentList(in_dir)
    
    # Each row represent a single examination code for a single patient. 
    # The code is saved in the convertedData file, if no error occurs.
    # Depending on the type of the code, the value or -990099 is saved.
    for row in rows:
        
        try:
            # Get ID, ICPC code and date (right format)
            key = int(row[ID_idx])
            ID_nhg = int(row[nhg_idx])
            ID_date = str2date(row[begin_idx],ymd=False)
            
            # If the code is zero or is not a real code, skip
            if ID_nhg == 0 or ID_nhg not in contentlist.keys():
                continue
            
            # If the date is not processed well, it returns an error.
            # This ensures that it loops to the except loop and will be processed later
            if (ID_date==-1):
                raise ValueError
                
            else:
                # Examination values are selected according to the type of examination.
                # For yes-types (JA), free text (VT), date-types (DT) or multiple-choice (MK), the value is not important.
                # Therefore, value is set unrealistic. It is saved which rows these were
                if contentlist[ID_nhg][14] == 'JA':
                    IDwaarde = -990099
                elif contentlist[ID_nhg][14] == 'DT' or contentlist[ID_nhg][14] == 'VT' or contentlist[ID_nhg][14] == 'MK':
                    VTDTMKdata.append({'gp_patidf': key, 'gp_exadate':ID_date, 'gp_exacod': ID_nhg, 'gp_waarde': row[waarde_idx]})  
                    IDwaarde = -990099
                
                # For numeric (NM) and single-choice (EK), the value is selected
                elif contentlist[ID_nhg][14] == 'EK' or contentlist[ID_nhg][14] == 'NM':
                    
                    # The value is altered a bit (such as removing spaces, see function)
                    try:
                        IDwaarde = alterValue(row[waarde_idx])
                    
                    # If the value is not clear, set the value as unrealistic (so it can be filtered when checking for value)
                    # However, when checking for the presence of codes, the code can be included
                    # Do indicate that this is wrongdata in a seperate files
                    except:
                        IDwaarde = -990099
                        wrongData.append({'gp_patidf': key, 'gp_exadate':ID_date, 'gp_exacod': ID_nhg, 'gp_waarde': row[waarde_idx]})  
                
                # If the codetype is different (such as empty), also save the code with an unrealistic value.
                else:
                    IDwaarde = -990099
                    emptyData.append({'gp_patidf': key, 'gp_exadate':ID_date, 'gp_exacod': ID_nhg, 'gp_waarde': row[waarde_idx]})
                
                # Include the code (independent of type) in the convertedData dict to save later on.
                # Here, the value is realistic or unrealistic (-990099), and can be filtered in the prepocessing step
                convertedData.append({'gp_patidf': key, 'gp_exadate':ID_date, 'gp_exacod': ID_nhg, 'gp_waarde': IDwaarde})  
        
        # It may occur that errors happened in the previous part.
        # These occur mainly due to free text in the file, screwing the read_csv file.
        # Therefore, this data is also saved, but processed later on more manually.
        except:
            falseData[falseDataCount]=row
            falseDataCount +=1
    
    # Save the different data type files
    out_dir_part = out_dir[0:out_dir.rfind('\\')]
    dictlistToCSV(wrongData, convertedDataHeader, out_dir_part + '\\gp_examination_wrong.csv')
    dictlistToCSV(VTDTMKdata, convertedDataHeader, out_dir_part + '\\gp_examination_VTDTMK.csv')
    dictlistToCSV(emptyData, convertedDataHeader, out_dir_part + '\\gp_examination_emptyType.csv')
    
    # Return both the good and the false data, as well as the header. The next function combines those
    return convertedData, convertedDataHeader, falseData
    
def convertFalseData(data, isold, manualCheck):
    # Converts not well processed data (such as due to free text) to well processed data
    # This is based on manual findings, so may not be universal. Therefore, manualcheck may be set to True; this will ask for confirmation
    
    # Initialize lists
    convertedGoodData = []
    
    # Each row is a row from the original csv while, which was wrong
    # Previously (isold), a certain way of processing was needed.
    # Now, an alternative way is selected
    for row in data.values():
        
        # The old way. 
        if isold:
            
            # Checks for " (which is free text) and selects the right part based on that
            if row[4][0]=='"':
                key1 = int(row[4].split(',')[4])
                ID_nhg1 = int(row[1])
                ID_date1 = str2date(row[4].split(',')[3], ymd=False)
                
                key2 = int(row[-2])
                ID_nhg2 = int(row[4].split(',')[-2])
                ID_date2 = str2date(row[-3],ymd=False)
                
                convertedGoodData.append({'gp_patidf': key1, 'gp_exadate':ID_date1, 'gp_exacod': ID_nhg1}) 
                convertedGoodData.append({'gp_patidf': key2, 'gp_exadate':ID_date2, 'gp_exacod': ID_nhg2}) 
            
            # If no free text, process differently
            else:
                key = int(row[-2])
                ID_nhg = int(row[1])
                ID_date = str2date(row[-3], ymd=False)
                convertedGoodData.append({'gp_patidf': key, 'gp_exadate':ID_date, 'gp_exacod': ID_nhg})
            
        # The new way. # For some reason, these columns should be used
        else:
            key = int(row[-2])
            ID_nhg = int(row[2])
            ID_date = str2date(row[0], ymd=False)
            IDwaarde = -990099
            convertedGoodData.append({'gp_patidf': key, 'gp_exadate':ID_date, 'gp_exacod': ID_nhg, 'gp_waarde': IDwaarde})
            
    # Output the converted files. If confirmation is needed, ask for confirmation before returning, otherwise just return it
    print('These files were converted incorrectly, this is the new output. Check if it seems right.')
    for row in convertedGoodData:
        print(row, '\n')
        
    if manualCheck==True:
        isgood = input('Y (Default) or N')
        
        if isgood!='N':
            return convertedGoodData
        
        else:
            return -1
    
    # Return the correctly converted data
    return convertedGoodData
 
def combineCorrectedData(dataToConvert, convertedData, manual_check, isold=False):
    # The convertData_nhg function return both good (convertedData) as incorrect (falseData or dataToConvert) data.
    # If dataToConvert is present, this function calls a correcting function and combines the correct and corrected data.
    # Returned data is a full and correct dataset, which can be saved
    
    # If all original data was already converted good
    if not dataToConvert:
        return convertedData
    
    # If errors existed, convert the false data and combine with the good data.s
    else:
        correctedData = convertFalseData(dataToConvert, isold, manual_check)
        convertedData.extend(correctedData)
        return convertedData

def findFilesInDir(dirPath, startString):
    # Return the files in the selected directory starting with the string
    listfiles = []
    for i in os.listdir(dirPath):
        if i.startswith(startString):
            listfiles.append(i)
    return listfiles
    
def processUitslagenFiles(in_dir, out_dir,manual_check = False):
    # Process raw examination files to a standard format. 
    # Data is divided into the sort examination (free text, numeric, etc), used for preprocessing.
    # Furthermore, the csv_read may not define columns right due to free text; this is fixed.
    
    # Select all files in the directory with the name 'Uitslagen' (one per year)
    listfiles = findFilesInDir(in_dir, 'Uitslagen')
    
    # Process each year of examination files
    for i in listfiles:
        print('Converting {}'.format(i))
        rows, fields = import_data(in_dir + '\\{}'.format(i))
        
        # Convert the data in the examination file to one format. For details,
        # see the function. In addition, if for some reason it did not work, this may be due to a fault in the raw file format.
        # This is tried to correct in the combineCorrectedData function
        convertedData, header, falseData = convertData_nhg(rows, fields, in_dir, out_dir)
        convertedData = combineCorrectedData(falseData, convertedData, manual_check)
        
        # The final convertedData dict is saved
        print('Saving {}'.format(i))
        dictlistToCSV(convertedData, header, out_dir)
        
        del convertedData, falseData
        