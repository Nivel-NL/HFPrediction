from .loadData import loaddata
import pandas as pd
import pickle

class makeDataSet():
    
    def __init__(self, name, in_dir, out_dir):
        self.out_dir = out_dir
        self.in_dir = in_dir
        self.name = name
        
    def loadData(self):
        # Load the baseline data, trend data, control data and the labels
        self.df, self.dfcontrol, self.trend, self.trendcontrol, self.y, self.y_extra = loaddata(self, True, percPres = 0.05, makeBinary = True, makeMonthsBinary = True, addtrend = True)
    
    def createDataset(self, dataToUse):
        # Identify one of six different datasets (see original article for included variables)
        if dataToUse == 'Set1':
            data = self.df[['age','gender']]
            data_extra = self.dfcontrol[['age','gender']]
        elif dataToUse == 'Set2':
            data = self.df.iloc[:,2::]
            data_extra = self.dfcontrol.iloc[:,2::]
        elif dataToUse == 'Set3':
            data = self.df[['age','gender']].join(self.df.iloc[:,2::], on = 'ID')
            data_extra = self.dfcontrol[['age','gender']].join(self.dfcontrol.iloc[:,2::], on = 'ID')
        elif dataToUse == 'Set4':
            data = self.trend.iloc[:,2::]
            data_extra = self.trendcontrol.iloc[:,2::]
        elif dataToUse == 'Set5':
            data = self.df[['age','gender']].join(self.trend.iloc[:,2::], on = 'ID')
            data_extra = self.dfcontrol[['age','gender']].join(self.trendcontrol.iloc[:,2::], on = 'ID')
        elif dataToUse == 'Set6':
            data = self.df[['age','gender']].join(self.df.iloc[:,2::], on = 'ID').join(
                self.trend.iloc[:,2::], on = 'ID', lsuffix="DROP").filter(regex="^(?!.*DROP)")
            data_extra = self.dfcontrol[['age','gender']].join(self.dfcontrol.iloc[:,2::], on = 'ID').join(
                self.trendcontrol.iloc[:,2::], on = 'ID', lsuffix="DROP").filter(regex="^(?!.*DROP)")
            
        return data, data_extra

    def getDataSetForLearning(self, setNumbers, toSave):
        # Obtain and save the dataset based on the set number
        
        for setNumber in setNumbers:
            dataSet, dataSetExtra = self.createDataset('Set{}'.format(setNumber))
            
            if toSave == True:
                
                with open('{}\\DataMatrix{}.pickle'.format(self.out_dir, setNumber),'wb') as handle:
                    pickle.dump([dataSet, self.y], handle, protocol=4)
                    
                with open('{}\\DataMatrix{}_extra.pickle'.format(self.out_dir, setNumber),'wb') as handle:
                    pickle.dump([dataSetExtra, self.y_extra], handle, protocol=4)
                    
            else:
                return dataSet,dataSetExtra
        
        return dataSet,dataSetExtra 
    

def collectData(dataname, dataset, toSaveData, in_dir, out_dir):
    # Here, the class is made, data loaded and processed.
    # Additional stuff could be implemented here
    maindata = makeDataSet(dataname, in_dir, out_dir)
    maindata.loadData()
    maindata.getDataSetForLearning(dataset, toSaveData)
    # Here, additional things can be implemented (correlation analysis, correlation with outcome, etc)
    return maindata
