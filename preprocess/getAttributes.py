#%% The number of occurences of medication, icpc and referrals are given in the selected interval.
#Note: lab results need references and do not yet work.

from datetime import timedelta
import re
from .StateInterval import StateInterval
from .utilDef import str2date

def generate_code(code, limit):
        '''generates the required part of the code in a field, 
            e.g. atc code A01 in field A01B234'''
        if code == None: 
            code = ''
        result = code.upper().strip()[0:limit]

        if result.lower() in ['oncologie', 'chirurgie', 'gastro-enterologie', 'interne geneeskunde', 'scopie-afdeling']:
            result = None

        return result
    
def generate_attributes(original_code, limit, suffix, src=''):
        '''Generate the attributes. In the most simple case
            this is a single attribute, namely the code + the 
            specified suffix.'''
        return [generate_code(original_code, limit) + '_' + suffix]
    
def init_key(d, k, v):
    '''initialises a default value v for a non-existing key k in a dictionary d'''
    if not k in d:
        d[k] = v
        
def four_weeks():
    return timedelta(weeks=4)
    
def getContentList(indir):
    # Return the diagnostic measurement information as content_list
    ind_str = indir.rfind('\\')
    new_filename = indir[0:ind_str+1] + 'Raw'
    file = open(new_filename + '\\NHG-Tabel 45 Diagnostische bepalingen - versie 34 - bepaling.txt','r')
    content = file.read()
    content_list_temp = content.split('\n')
    del content_list_temp[0]
    header = content_list_temp[0].split('\t')
    del content_list_temp[0]
                                 
    content_list={}
    
    for row in content_list_temp:

        content_list[int(row.split('\t')[0])] = row.split('\t')

    return content_list

def getRefValue(value, original_code, contentlist, kind_value):
    # Get the reference value for diagnostic measurements.
    
    # Basics
    refmin_id = 19
    refmax_id = 20
    code_id = 14
    refvalue = 0
    
    # Define a manual list (called manual)
    manual_list = ['1966','3850','3851','1968']
    
    # For the baseline, just indicate wheter it is present, so return the code
    if kind_value=='base':
        if str(original_code) in manual_list:
            refvalue = 'BNP'
        else:
            refvalue = str(original_code)
        return refvalue
    
    # For trends, don't use non-true measurements (=-990099)
    if ((float(value) < -990098) and (float(value) >-990100)) or (original_code not in contentlist):
        refvalue=0
        return refvalue
    
    # Again, manual
    if str(original_code) in manual_list:
        refvalue = 'BNP'
        return refvalue
    
    # Make reference values: can be absolute or relative
    # Absolute indicates whether the value is above the refvalue specified in the diagnostic file
    elif kind_value=='abs_ref':
        if contentlist[original_code][code_id] == 'NM':
            value  = float(value)
            if (contentlist[original_code][refmin_id]=='') and (contentlist[original_code][refmax_id]==''):
                refvalue = 'NM' + 'noref'
            elif (contentlist[original_code][refmin_id]!='') and (value < float(contentlist[original_code][refmin_id].replace(',','.'))):
                refvalue = 'NM' + 'low'
            elif (contentlist[original_code][refmax_id]!='') and (value> float(contentlist[original_code][refmax_id].replace(',','.'))):
                refvalue = 'NM' + 'high'
            else:
                refvalue = 'NM' + 'norm'
                
                
        elif contentlist[original_code][code_id] == 'EK':
            refvalue = 'EK' + value
    
    # Relative just saves the value, which is altered in a later piece of code relative to other measurements
    elif kind_value=='rel_ref':
        if contentlist[original_code][code_id] == 'NM':
            refvalue = 'NM' + str(value)
        elif contentlist[original_code][code_id] == 'EK':
            refvalue = 'EK' + value   
    
    return refvalue

def insert_state_interval(id2data, key, state, begin, end, original_code, src):
        '''converts state-begin-end-triples to state intervals, add to data record data'''
        sequence = id2data[key]['data']
        SI = StateInterval(state, begin, end)
        sequence.append(SI)
        return sequence

def insert_data(info,rows, headers, code_column, date_column, regex_string, limit, suffix='', incorporate_SOEP=False):
        '''inserts data from the specified csv and corresponding columns'''

        # make convenient reference to the dictionary
        dct = info.id2data
        
        # get the index of the relevant columns
        ID_idx = headers.index(info.ID_column)
        code_idx = headers.index(code_column)
        b_date_idx = headers.index(date_column[0])
        e_date_idx = headers.index(date_column[1])
        
        if suffix == 'lab':
            waarde_idx = headers.index('gp_waarde')
            content_list = getContentList(info.in_dir)
        
        # get the right suffix to append for the attribute name
        if suffix == '':
            suffix = code_column
        
        # regex pattern to match (ATC/ICPC standards)
        pattern = re.compile(regex_string)
        
        # iterate over all instances, making a new dict with the new attributes as keys
        attribute2ids = dict()
        
        # Check for continous medication
        dict_atc = {}
            
        for row in rows:
        
            # if key is not in the data dictionary, we skip it
            key = int(row[ID_idx])
            if not key in dct:
                continue
        
            # init other vars
            b_date = str2date(row[b_date_idx], ymd=True, give_default_begin=True) # beginning data
            e_date = str2date(row[e_date_idx], ymd=True, give_default_end=True) # ending data
            b_reg = dct[key]['dis_dates'][3] # beginning of registration
            e_reg = dct[key]['dis_dates'][4] # ending of registration
        
            original_code = row[code_idx]
            if original_code == None:
                continue
            
            truncated_code = generate_code(original_code, limit)
            if truncated_code == None:
                continue
            
            # This is irrelevant ICPC code
            if truncated_code=='Q00':
                continue
            
            # Set chronic codes to the right time
            if suffix == 'chronic':
                
                if b_date < e_reg:
                    b_date = b_reg
                    e_date = b_reg
                
                else:
                    continue
        
            # To generate baseline data (without patterns)
            if info.baseline == True:
                
                if (b_reg <= b_date and b_date <= e_reg) and pattern.match(truncated_code):
                
                    if suffix == 'lab': # if we prepare for lab result abstraction
                        
                        # Get the right refvalue
                        value = row[waarde_idx]
                        refvalue = getRefValue(value, int(original_code), content_list, info.kind_lab)
                        if refvalue == 0:
                            continue
                        
                        attributes = generate_attributes(refvalue, limit, suffix, src=code_column)
                        
                    elif suffix != 'lab':
                        attributes = generate_attributes(original_code, limit, suffix, src=code_column)
                       
                    for attr in attributes:
                        init_key(attribute2ids, attr, dict())
                        init_key(attribute2ids[attr], key, 0)
    
                        # add 1 to the occurrence of the attribute in the instance
                        attribute2ids[attr][key] += 1
            
            # To generate data for pattern recognition
            elif info.baseline == False:
                
                if suffix == 'atc':
                    # Check if medication is present -180 days to +90 days after begin data
                    b_reg_dy = b_reg - timedelta(days=180)
                    e_reg_dy = b_reg + timedelta(days=90)
                    
                    # Make a dict with the count of medication in the selected interval per patient
                    # Will be checked later as chronic medication
                    if (b_reg_dy <= b_date and b_date <= e_reg_dy) and pattern.match(truncated_code):
                        if key not in dict_atc.keys():
                            dict_atc[key]={}
                        if truncated_code not in dict_atc[key].keys():
                            dict_atc[key][truncated_code] = 0
                        dict_atc[key][truncated_code]=dict_atc[key][truncated_code]+1
                    
                # if in the required interval and code is valid
                if ( (b_reg <= b_date and b_date <= e_reg) or (b_reg <= e_date and e_date <= e_reg) ) and pattern.match(truncated_code):
                    
                    if suffix == 'lab': # if we prepare for lab result abstraction
                        
                        # Get the right reference value
                        value = row[waarde_idx]
                        refvalue = getRefValue(value, int(original_code), content_list, info.kind_lab)
                        if refvalue == 0:
                            continue
                        
                        if refvalue == 'BNP':
                            attributes = generate_attributes(refvalue, limit, refvalue, src=code_column)
                        else:
                            attributes = generate_attributes(original_code, limit, refvalue, src=code_column)
        
                    # else no lab result collection, regular aggregation
                    elif suffix != 'lab':
                        attributes = generate_attributes(original_code, limit, suffix, src=code_column)
    
                    for attr in attributes:
                        # check if attribute name and ID instance already exist, if not, make them
                        sequence = insert_state_interval(info.id2data,key, attr, b_date, e_date, original_code, code_column)
                        info.id2data[key]['data'] = sequence
                        
        if info.baseline==True:
            # add data to each instance
            for ID in dct:
                data = dct[ID]['data']
            
                for id2occurrences in attribute2ids.values():
                    
                    # if patient has occurrences for the attribute, add that number, else add 0
                    if ID in id2occurrences: 
                        data.append(id2occurrences[ID])
                    else:
                        data.append(0)
                        
        if suffix == 'atc':                
            info.medCount = dict_atc
       
        # return the keys to be used as headers when writing the processed data
        return attribute2ids.keys()

    
def get_attributes(info, rows, fields, attr):
    #if 'medication' in needs_processing and needs_processing['medication']:
    print('...processing {}'.format(attr))
    if attr == 'medication':
        new_headers = insert_data(info,
                                rows, fields, 
                                'gp_medatc', 
                                ['gp_medprd', 'gp_medprd'], 
                                '[A-Z][0-9][0-9]', 3,
                                suffix='atc')
        
    elif attr == 'examination':
        new_headers = insert_data(info,
                                rows, fields, 
                                'gp_exacod', 
                                ['gp_exadate', 'gp_exadate'], 
                                '.+', None,
                                suffix='lab')
                                
    elif attr == 'episodes':
        new_headers = insert_data(info,
                                rows, fields, 
                                'gp_epsicpc', 
                                ['gp_epssince', 'gp_epssince'], 
                                '[A-Z][0-9][0-9]', 3)
        
    elif attr == 'chronic':
        new_headers = insert_data(info,
                                rows, fields, 
                                'gp_epsicpc', 
                                ['gp_epssince', 'gp_epssince'], 
                                '[A-Z][0-9][0-9]', 3,
                                suffix = 'chronic')
        
    else:
        print('Code is not recognized (no episodes, examination or medication')
        return
    
    info.headers = info.headers + list(new_headers) 
   