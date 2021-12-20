#%% Make trends from the trend lab values

import numpy as np

def maketrendsfromlab(info, pfactor = 0.05):
    
    allNM = {}
    
    for pat in info.id2data.keys():
            
            # Select data from a single patient
            p = info.id2data[pat]['data']
            
            # Length of 4 indicates no data
            if len(p)==4:
                continue
            
            tempNM = {}
            
            # For each data instance
            for ind,i in enumerate(p[3:-1]):
                # Check if NM is present, meaning a numeric lab value.
                # If it is NM, select the code, and add the value for the code 
                if i.state.find('_NM')!=-1:
                    code = i.state[0:i.state.find('_NM')]
                    if code in tempNM.keys():
                        tempNM[code].append(float(i.state[i.state.find('_NM')+3::]))

                    else:
                        tempNM[code] =[ float(i.state[i.state.find('_NM')+3::])]
            
            # Save the mean of all numeric values for a single code per patient
            for u in tempNM.keys():
                temp = np.mean(tempNM[u])
                if u in allNM.keys():
                    allNM[u].append(temp)
                else:
                    allNM[u] = [temp]
    
    # Save the 5, 95 perc and the mean (for calculation of the first value)
    # Additionally, save the change from the previous value which may be present
    for i in allNM.keys():
        allNM[i] = [np.percentile(allNM[i],5), np.percentile(allNM[i],95), np.mean(allNM[i])]
        allNM[i].append(pfactor*(allNM[i][1]-allNM[i][0]))

                
    for pat in info.id2data.keys():
            
            # Select data from a single patient
            p = info.id2data[pat]['data']
            
            # Length of 4 indicates no data
            if len(p)==4:
                continue
            
            NMdict = {}
            NMindex = {}
            removeNM = []
            
            # For each data instance
            for ind,i in enumerate(p[3:-1]):
                # Check if NM is present, meaning a numeric lab value.
                # If it is NM, select the code, and add the value for the code
                # Also, add the index for each NM data instance (for removal)
                if i.state.find('_NM')!=-1:
                    code = i.state[0:i.state.find('_NM')]
                    if code in NMdict.keys():
                        NMdict[code].append(float(i.state[i.state.find('_NM')+3::]))
                        NMindex[code].append(ind)
                    else:
                        NMdict[code] =[ float(i.state[i.state.find('_NM')+3::])]
                        NMindex[code] = [ind]
                     
            # Per code in a patient, select the NM values
            for u in NMdict.keys():
                i = NMdict[u]
                
                # Select the max deviation and the mean value over the population
                difmax = allNM[u][3]
                meanNM = allNM[u][2]
                
                # Make a new list with lab references as up/down/norm
                labToRef = []
                
                # for each NM value (with the same NM code), check deviations
                for ind, j in enumerate(i):
                    # The first NM value is checked to the mean of the population
                    if ind==0:
                        if (j > meanNM+difmax):
                            labToRef.append('up')
                        elif (j < meanNM-difmax):
                            labToRef.append('down')
                        else:
                            labToRef.append('norm')
                        continue
                    
                    # Check each NM value compared to the previous value
                    if (j > i[ind-1]+difmax):
                        labToRef.append('up')
                    elif (j < i[ind-1]-difmax):
                        labToRef.append('down')
                    else:
                        labToRef.append('norm')
                
                # Save in the NMdict under the code the replaced values
                NMdict[u] = labToRef
                
            # For each selected index per code   
            for i in NMindex.keys():
                for ind,j in enumerate(NMindex[i]):
                    # Replace the value in the dataset with the code + the ref
                    p[j+3].state = i + '_' + NMdict[i][ind]
            
            # This enables removal, although in this file this is not done
            # Therefore, this just inserts the values in the complete dataset
            l = [x for x in p[3:-1] if x.state.find('to_remove')==-1]
            info.id2data[pat]['data'] = p[0:3] + l + [p[-1]]
     
            
#%% Divide time in seperate intervals (12 pieces)

def divideIntervals(info):
    import datetime
    import math
     
    if info.n_section==None:
        return
    
    for pat in info.id2data.keys():
            
            p = info.id2data[pat]['data']
            
            if len(p)==4:
                continue 
            
            # Select the begin, end and number of days per section
            begindate = info.id2data[pat]['dis_dates'][3]
            enddate = info.id2data[pat]['dis_dates'][4]
            totaldays = round((enddate-begindate)/datetime.timedelta(days=1))
            sectiondays = totaldays / info.n_section
            
            toremove = []
            for ind, i in enumerate(p):
                # Dont use the first 3 or last, as this is not data
                if ind<3 or ind==len(p)-1:
                    continue
                
                # Sets the dates as the first date in a region
                p[ind].begin = enddate - datetime.timedelta(days = (math.ceil(((enddate-i.begin)/sectiondays)/datetime.timedelta(days=1)))*sectiondays)
                p[ind].end = enddate - datetime.timedelta(days = (math.ceil(((enddate-i.begin)/sectiondays)/datetime.timedelta(days=1)))*sectiondays)
                
                # If the same pattern and date is already present in the previous parts, remove this one (no doubles)
                for j in range(3, ind):
                    if (p[j].state == p[ind].state) and (p[j].begin == p[ind].begin) and (p[j].end == p[ind].end):
                        toremove.append(p[ind])
            
            # Save the data
            p = [x for x in p if x not in toremove]
            info.id2data[pat]['data'] = p
            
#%% Set target as last header in header list and data list

def move_target_to_end_of_list(info):
    '''moves first data value to end of list for each instance in data dictionary'''
    print('...correctly positioning the target attribute')

    for k in info.id2data:
        data = info.id2data[k]['data']
        data.append(data.pop(0))

#%% Sort sequences according to begin and end
def sort_sequences(id2data):
        '''sort each state sequence (= 1 per patient) consisting of state intervals
             order of sort is: begin date->end date->lexical order of state name'''
        from operator import attrgetter
        for k in id2data:
            sequence = id2data[k]['data']
            static_seq = sequence[0:3] # gender/age
            dynamic_seq = sequence[3:-1]
            dynamic_seq.sort(key=attrgetter('begin', 'end', 'state'))
            dis = [sequence[-1]]
            id2data[k]['data'] = static_seq + dynamic_seq + dis
            
        return id2data 
 
#%% Select which medication is chronic

def getContinuousMed(info):
    # Check if medication is chronic (at least 3 times in a timespan)
    
    for pat in info.id2data.keys():
            
            p = info.id2data[pat]['data']
            
            if len(p)==4:
                continue 
            
            if pat not in info.medCount.keys():
                continue                        
            
            remove_atc = []
            ind_remove = []
            day_atc= []
            
            for ind,i in enumerate(p):
                # Dont use the first 3 and the last (other data)
                if ind<3 or ind==len(p)-1:
                    continue
                
                # Select the medication code if it is present in medCount
                if i.state[-7:-4] in info.medCount[pat].keys():
                    # If more than 2 times present, indicate that this code has to be removed
                    # If this was not the first time, select the index
                    if info.medCount[pat][i.state[-7:-4]]>2:
                        if i.state[-7:-4] in remove_atc:
                            ind_remove.append(ind)
                        else:
                            remove_atc.append(i.state[-7:-4])
                            day_atc.append(ind)
                      
            # Set each first code to the first date (thus registration date)
            for i in day_atc:
                p[i].begin =  info.id2data[pat]['dis_dates'][3]
                p[i].end = info.id2data[pat]['dis_dates'][3]
            
            # Select only those which should not be removed (thus the double codes)
            l = [p[x] for x in range(0,len(p)) if x not in ind_remove]
            
            info.id2data[pat]['data'] = l