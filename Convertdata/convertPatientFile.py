# Functions to
# 1. (getGoodPrak) select GPs with at least 3 consecutive years 
# 2. (convertPatient) select patients with at least 3 years of data and save the (un)registration dates
from .io_data import dictlistToCSV
import numpy as np
import pickle
            
def getGoodPrak(rows, headers):
    # Select only the GP practices with at least three consecutive years without error.
    # Without error is stated as no fault in journal, prescription, icpc or chronic (see patient file).
    # Returns a dictionary with the GP id as keys, with per GP id the years corresponding to the maximum consecutive years (minimal 3)
    
    num_good_years = 3 # (means 3 good years)
    
    # Initialize the indexes of the headers
    prak_idx = headers.index('randompraknr')
    jaar_idx = headers.index('jaar')
    blok_idx1 = headers.index('journaal')
    blok_idx2 = headers.index('prescriptie')
    blok_idx3 = headers.index('uitslagen')
    blok_idx4 = headers.index('ziekte_epi')
    
    # Initialize needed empty lists
    all_prak = []
    fault_prak = []
    all_prak_dict={}
    all_prak_dict_year={}
    
    # Each row represent a single year for a single GP office. If this row is after 2011 and without error,
    # append the year to the corresponding GP id in all_prak_dict, which saves for each GP which years can be used. 
    for row in rows:
        
        # Selecting only years without error and after 2011
        if ((row[blok_idx1]!="Nee" and
            row[blok_idx2]!="Nee" and
            row[blok_idx3]!="Nee" and
            row[blok_idx4]!="Nee") and
            int(row[jaar_idx])>2011):
            
                # Add years to be used at the GP ind in the dict
                if int(row[prak_idx]) not in all_prak_dict.keys():
                    all_prak_dict[int(row[prak_idx])] = [int(row[jaar_idx])]
                else:
                    all_prak_dict[int(row[prak_idx])].append(int(row[jaar_idx]))
    
    # A GP can be included if at least 3 consecutive good years are available.
    # Therefore, if at least 3 years are present in the dictionary, the number of consecutive years are calculated.
    # The years corresponding to the maximumum are then selected
    for i in all_prak_dict.keys():
        
        # Only proceed if 3 years or more are present
        if len(all_prak_dict[i])>=num_good_years:
            count=[[]]
            tel=0
            
            # Create per GP a list with consecutive years
            for j in all_prak_dict[i]:
                if count[tel]==[]:
                    count[tel].append(j)
                else:
                    if j-count[tel][-1]==1:
                        count[tel].append(j)
                    else:
                        tel = tel+1
                        count.append([j])
                        
            # Select the list with the maximum length and save in dict with GP ind as key
            if len(max(count, key=len))>=num_good_years:
                all_prak_dict_year[i] = max(count, key=len)
            
    return all_prak_dict_year


def convertPatient(rows, headers, good_prak, savefile):
    # Select patient with at least three years of data
    # Of these patients, save the (un)registration dates, which are the first and last available data dates.    
    # Based on these dates, in the preprocessing part a segment of data will be selected.
    
    num_good_years = 3
    
    # Initialize the indexes of the headers
    ID_idx = headers.index('randompatnr')
    prak_idx = headers.index('randompraknr')
    age_idx = headers.index('geboortejaar')
    gender_idx = headers.index('geslacht')
    begin_idx_jaar = headers.index('jaar')
    begin_idx_kwartaal = headers.index('minkwartaal')
    begin_idx_eindkwartaal = headers.index('maxkwartaal')
    
    # Set what the headers of the file to create will be
    convertedDataHeader=['gp_patidf', 'gp_patyob', 'gp_patgen', 'gp_entree','gp_exit', 'gp_praknr']
    
    # Initialize empty dicts
    convertedData = dict()
    patInPrak = dict()
    yearPerPat = dict()
    
    # Set each quarter to the corresponding month (beginning)
    quart = {'1': 1, '2': 4, '3': 7, '4': 10}
    
    # Each row represent a single year for a single patient. 
    # The first and last year with data is selected, as well as some demographics.
    for row in rows:
        
        # Get ID, age, gender and prak ID of patient
        key = int(row[ID_idx])
        ID_age = int(row[age_idx])
        ID_gen = 'M' if row[gender_idx]=='Man' else 'V'
        ID_prak = int(row[prak_idx])
        
        # If the GP office is not selected as good, exclude the patient
        if ID_prak not in good_prak.keys():
            continue
            
        # Only use this row if it is in the years selected for the GP office
        # Based on this row, if necessary, the (un)registration dates are updated
        if int(row[begin_idx_jaar]) in good_prak[ID_prak]:
            
            # Select the year and quarters
            beginjaar = row[begin_idx_jaar]
            minkwartaal = row[begin_idx_kwartaal]
            maxkwartaal = row[begin_idx_eindkwartaal]
            
            # If there is already data on registration, check if it has to be updated.
            # Otherwise, the data has to be used for registration
            if key in patInPrak:
                if min(patInPrak[key][0],beginjaar) == beginjaar:
                    patInPrak[key][0] = beginjaar
                    patInPrak[key][1] = minkwartaal
                    
                if max(patInPrak[key][2],beginjaar) == beginjaar:
                    patInPrak[key][2] = beginjaar
                    patInPrak[key][3] = maxkwartaal
                    
            else:
                patInPrak[key] = [beginjaar, minkwartaal, beginjaar, maxkwartaal]
                yearPerPat[key] = []
            
            # Save the years included
            yearPerPat[key].append(beginjaar)
            
        # Each time, also update the convertedData. This is a dict with for each patient the
        # demographics and the final registration and unregistration date
        if key in patInPrak:
            registration = '1-{}-{}'.format(str(quart[patInPrak[key][1]]), str(patInPrak[key][0]))
            
            # Unregistration has different final end days (30 or 31) per month
            if (int(patInPrak[key][3]) == 2) or (int(patInPrak[key][3]) == 3):
                unregistration = '30-{}-{}'.format(str(quart[patInPrak[key][3]]+2), str(patInPrak[key][2]))
           
            else:
                unregistration = '31-{}-{}'.format(str(quart[patInPrak[key][3]]+2), str(patInPrak[key][2]))
            
            # Update the convertedData dict
            convertedData[key] = [ID_age, ID_gen, registration, unregistration, ID_prak]

    # Here, the convertedData is completed, consisting of a single entry per patient
    # However, at least three years have to be present.
    # Remove if patient length < 3
    to_remove=[]
    for pat in yearPerPat.keys():
        if len(yearPerPat[pat])<num_good_years:
            to_remove.append(pat)
            
    for key in to_remove:
        del convertedData[key]
        del yearPerPat[key]
    
    # Save the remaining patients as a dict per pat in a list, which is the format for the save function
    convertedDataNew = []
    for i in convertedData.keys():
        convertedDataNew.append({'gp_patidf': i, 'gp_patyob':convertedData[i][0], 'gp_patgen': convertedData[i][1],
                                 'gp_entree': convertedData[i][2], 'gp_exit':convertedData[i][3], 'gp_praknr': convertedData[i][4]})
    
    # Save the patients demographics and the registration dates to a csv file
    dictlistToCSV(convertedDataNew, convertedDataHeader, savefile)
    
    # Also save the years per pat, if it is necessary.
    #f= open(savefile[:-4] + '_years', 'wb')
    #pickle.dump(yearPerPat, f)
    #f.close()