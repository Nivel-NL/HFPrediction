import numpy as np
import pandas as pd
import pickle
from .generatePattern import generate
from .StateSequence import StateSequence
#from .StateInterval import StateInterval


def stateToName(pattern):
    name = ''
    for u in pattern.states:
        if name=='':
             name = name  + u
        else:
            name = name + '_' + u
    for uu in range(1, len(pattern.relations)):
        name = name + pattern.relations[uu-1, uu].decode('UTF-8')
    return name

def make_state_sequence(record):
    '''recreates the state sequence used when mining for frequent patterns'''
    patient = record[0]
    birthyear = record[1]
    gender = record[2]
    patterns = record[3:-1]
    dis = record[-1]
    #for i in range(len(patterns)):
    #    pass
        #if type(patterns[i]) != StateInterval:
        #    str_SI = patterns[i].split(';')
        #    patterns[i] = StateInterval(str_SI[0], str_SI[1], str_SI[2])
    return StateSequence(patterns, str(patient), gender, birthyear, dis)

def makeStateSequence(pat, patternlist):
    # Make a state sequence file
    SS = make_state_sequence(pat)
    
    patient = SS.patient
    gender = SS.gender
    birthyear = SS.birthyear
  
    patternsFound = [stateToName(pattern) for pattern in patternlist if SS.covered_by(pattern)]
    
    return patternsFound
        
def makeDF(trends, id2data2):
    # Generate a DF with the proper size and info
    
    colnames = []
    for i in trends:
        name = ''
        for u in i.states:
            if name=='':
                 name = name  + u
            else:
                name = name + '_' + u
        for uu in range(1, len(i.relations)):
            name = name + i.relations[uu-1, uu].decode('UTF-8')
        colnames.append(name)
        
    keys = id2data2.keys()
    df = pd.DataFrame(0, index = keys, columns = colnames)
    ispos = []
    age=[]
    gender=[]
    ID = []
    for i in id2data2.values():
        if i['data'][-1]=='positive':
            ispos.append(i['data'][0])
        ID.append(i['data'][0])
        age.append(i['data'][1])
        if i['data'][2]=='V': gender.append(1) 
        else: gender.append(0)
    df['target'] = 0
    df.loc[ispos, 'target'] = 1
    
    dfnew = pd.DataFrame(data = {'age':age, 'gender':gender}, index = ID, columns=['age', 'gender'])
    df = dfnew.join(df)
    
    return df


def fillDF(df, trends, id2data2):
    # Fill the DF with the patterns (present in which patient)

    for pat in id2data2.values():
        
        patternsPat = makeStateSequence(pat['data'], trends)
        
        if patternsPat!=[]:
            df.loc[pat['data'][0] , patternsPat] = 1

    return df

     
def makePattern(info, patterndata, pattern_cutoff = 0.1, gen_pat = False):
    
    # If loaddata is set, the patterns are already generated (saves a lot of time)
    # For now, we only select the positive trends
    
    # For below: a represents all trends, both pos and neg, above the min_sup threshold.
    if gen_pat == False:
        with open(patterndata,'rb') as handle:
            pos_neg = pickle.load(handle)
            a = pos_neg[2]
            
    else:
        # Calculate the trends for positive and negative cases
        a,b,c = generate(info.id2data, pattern_cutoff) 
        
        # Trends positive cases, sorted on support
        pos_trend = [x for x in a if x not in c] 
        f = [x.support for x in pos_trend]
        f = np.flipud(np.argsort(f))
        pos_trend = [pos_trend[x] for x in f]
        
        # Trends negative cases, sorted on support
        neg_trend = [x for x in a if x not in b]
        f = [x.support for x in neg_trend]
        f = np.flipud(np.argsort(f))
        neg_trend = [pos_trend[x] for x in f]
        
        # Combined trends, save to a pickle
        pos_neg = [pos_trend, neg_trend, a, b, c]
        
        with open(patterndata,'wb') as handle:
            pickle.dump(pos_neg, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Create a dataframe and fill it with the trends present in patients
    df = makeDF(a, info.id2data)
    df = fillDF(df, a, info.id2data)
    return df
             