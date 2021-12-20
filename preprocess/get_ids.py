from .utilDef import str2date

def get_IDs(info, rows, headers):
    # Set all IDs as keys in a dict. Add in a 'data' list in dict the key, age and gender
    # Add in a 'dis_dates' list the registration and unregistration dates of a patient in the GP clinic
    # Future interval selection will select within this interval
    
    print('...getting all record IDs')
    
    # Initialize the indexes of the headers
    ID_idx = headers.index(info.ID_column)
    age_idx = headers.index('gp_patyob')
    gender_idx = headers.index('gp_patgen')
    begin_idx = headers.index('gp_entree')
    end_idx = headers.index('gp_exit')

    # Each row represent a single patient. 
    # The id, age and gender are saved in a dict per person.
    # Case/control is now set to 'negative' for all patients; is done later
    for row in rows:
        
        # Select the ID and age
        key = int(row[ID_idx])
        ID_age = int(row[age_idx])

        # val is a new dict with keys 'data' and 'dis_dates',
        # containing the processed data and registration dates for one patient
        val = dict()
        val['data'] = ['negative', key, ID_age, row[gender_idx]]

        registration = str2date(row[begin_idx], ymd=False, give_default_begin=True)
        unregistration = str2date(row[end_idx], ymd=False, give_default_end=True)
        val['dis_dates'] = ['negative', registration, unregistration]
        
        # add dict to the greater overarching dict
        info.id2data[key] = val
    
    # Save headers
    info.headers = ['ID', 'age', 'gender']

