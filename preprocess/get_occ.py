from .utilDef import str2date
import re

def get_dis_occurrences(info, rows, headers):
    # Check whether a selected patient has the selected icpc code (case).
    # If the patient is a case, save the first date; otherwise, save "negative"
    
    print('...getting all target ({}) occurrences'.format(info.disCode))

    # Initialize the indexes of the headers
    ID_idx = headers.index(info.ID_column)
    dis_idx = headers.index('gp_epsicpc')
    date_idx = headers.index('gp_epssince')

    # Set the regex pattern to match icpc code to (i.e. K77)
    dis_pattern = re.compile(info.disCode)

    # iterate over all data to check for dis cases
    for row in rows:
        
        # Select the ID
        key = int(row[ID_idx])
        
        # Check if key is in dict
        if key in info.id2data:
            
            # Get the diagnosis date; is 'negative' if none (yet)
            dis = info.id2data[key]['dis_dates'][0]
            
            # get ICPC code (length 3) and its date
            code = row[dis_idx]
            if code == None:
                continue
            elif type(code) == str:
                code = code.strip().upper()[0:3]

            code_date = str2date(row[date_idx], ymd=True)

            # add dis case if code matches, AND corresponding date is earlier than the currently recorded
            # This saves to the overarching dict (id2data)
            if dis_pattern.match(code) and (dis == 'negative' or dis > code_date):
                info.id2data[key]['dis_dates'][0] = code_date
                info.id2data[key]['data'][0] = 'positive'