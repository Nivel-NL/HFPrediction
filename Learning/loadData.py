import pandas as pd
import numpy as np

def loaddata(info, extraControls, percPres = 0.05, makeBinary = True, addtrend = False):
    
    # Load the preprocessed data
    df_full = pd.read_csv(info.in_dir + '\\Baseline_' + info.name + 'month.csv')
    df = df_full.copy().filter(regex = 'ID|age|gender|[^ref]$', axis=1)
    if makeBinary == False:
        df_nonbin = df.copy()
    
    # For counts yes/no, set as bool values
    df.iloc[:,3:-1] = df.iloc[:,3:-1].astype(bool)  

    # Select the parameters which occur less than 5% and drop them
    countlistC = df.loc[df['target']==0].sum() / df.loc[df['target']==0].count()
    countlistC = (countlistC<percPres)
    countlistP = df.loc[df['target']==1].sum() / df.loc[df['target']==1].count()
    countlistP = (countlistP<percPres)
    
    if makeBinary==False:
        df = df_nonbin
    
    # Drop the parameters
    df.drop([x for x in countlistP.index if countlistP[x] == True 
              and countlistC[x] == True], axis=1, inplace = True)
    
    # Identify the labels
    y = df[['ID','target']]
    y.set_index('ID', inplace = True)
    df.drop(['target'],axis=1,inplace = True)

    del df_full
    try:
        del df_nonbin
    except:
        pass
    
    # Save the parameters for loading the controls
    collist1 = df.columns.tolist()
    df.set_index('ID', inplace = True)
    
    # Add a trend dataset
    trend=[]
    if addtrend == True:
        trend = pd.read_csv(info.in_dir + '\\Trend_' + info.name + 'month.csv')
        trend.iloc[:,3:-1] = trend.iloc[:,3:-1].astype(bool)
        trend.drop(['target'],axis=1,inplace = True)
        collist2 = trend.columns.tolist()
        
        trend.set_index('ID', inplace = True)
        
        # Add the month counts
        trend = trend.join(df.iloc[:,2:6], on = 'ID')
        
    dfcontrol = df.copy().iloc[[1]]
    dfcontrol.target = -1
    
    if extraControls == True:
    
        # Load saved data for extra controls
        collist1.append('target')
        dfcontrolfull = pd.read_csv(info.in_dir + '\\BaselineExtraPatients_' + info.name + 'month.csv',sep=',', usecols = collist1)[collist1]
        dfcontrol = dfcontrolfull.copy().filter(regex = 'ID|age|gender|[^ref]$', axis=1)
        
        if makeBinary == True:
            # For counts yes/no, set as bool values
            dfcontrol.iloc[:,3:-1] = dfcontrol.iloc[:,3:-1].astype(bool)
        
        # Identify the labels (all zeros)
        y_extra = dfcontrol[['ID','target']]
        y_extra.set_index('ID', inplace = True)
        dfcontrol.drop(['target'],axis=1,inplace = True)
        
        del dfcontrolfull
        
        dfcontrol.set_index('ID', inplace = True)
        
        # Add trend of controls
        trend_extra = []
        if addtrend == True:
            trend_extra = pd.read_csv(info.in_dir + '\\TrendExtraPatients_' + info.name + 'month.csv', usecols = collist2)[collist2]
            trend_extra.iloc[:,3::] = trend_extra.iloc[:,3::].astype(bool)  
            trend_extra.set_index('ID', inplace = True)
            trend_extra = trend_extra.join(dfcontrol.iloc[:,2:6], on = 'ID')
        
        # Drop where indices are the same for normal and extra controls
        n = set(list(df.index.values))
        p = set(list(dfcontrol.index.values))
        SameInd = list(n.intersection(p))
        y_extra.drop([x for x in list(dfcontrol.index.values) if x in SameInd], inplace = True)
        dfcontrol.drop([x for x in list(dfcontrol.index.values) if x in SameInd], inplace = True)
        trend_extra.drop([x for x in list(trend_extra.index.values) if x in SameInd], inplace = True)
    
    return df, dfcontrol, trend, trend_extra, y, y_extra 