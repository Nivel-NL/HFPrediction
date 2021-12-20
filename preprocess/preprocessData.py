from .io_data import import_data
from .get_ids import get_IDs
from .get_occ import get_dis_occurrences
from .getInterval import insert_data_intervals
from .getCaseControl import getcasecontrol
from .getNumberJournalLines import getjournallines
from .getAttributes import get_attributes
from .preprocess_func import divideIntervals, move_target_to_end_of_list, sort_sequences, maketrendsfromlab, getContinuousMed
from .makepattern import makePattern
from .saveData import save_output
import os

class preProcessing():
    # Convert raw data into csv files which can be preprocessed and be used for feature extraction
    # Class consist of numerous functions, which except from ICPCcounts can be processed seperately.
    
    def __init__(self, icpc, in_dir, out_dir, numextra, interval, name, trendname, kind_lab,n_section, baseline, toprocess):
        self.in_dir = in_dir
        self.delim = ','
        self.out_dir = out_dir
        self.ID_column = 'gp_patidf' 
        self.interval = interval
        self.id2data = dict() # dict describing all data instances
        self.to_process = toprocess
        self.matchAgeSex = False # If True, the algorithm matches based on Age and Sex
        self.baseline = baseline
        self.disCode = icpc
        self.numControls = 1
        self.NumExtraSamples = numextra
        self.name = name
        self.trendname = trendname
        self.kind_lab=kind_lab
        self.n_section=n_section
        self.minAge = 70
    
    def getid(self): 
        # Get the ID from each patient and save this in the id2data dict.
        # In addition, save age and gender as well as (un)registration date
        
        rows, fields = import_data(self.in_dir + '\\gp_patient.csv', delim=self.delim)
        get_IDs(self, rows, fields)
        
    
    def getocc(self):
        # Check whether a selected patient has the selected icpc code (case).
        # If the patient is a case, save the first date; otherwise, save 'negative'
        
        rows, fields = import_data(self.in_dir + '\\gp_episodes.csv', delim=self.delim)
        get_dis_occurrences(self, rows, fields)
        
    
    def getint(self):
        # Selects per patients the interval for which data is used.
        # Algorithm updates the existing overarching id2data with begin and end interval in the dates list
        
        insert_data_intervals(self)
    
    #%% Get cases and controls, matched if necessary, or extra controls
    
    def getcasesandcontrols(self):
        
        rows, fields = import_data(self.in_dir + '\\gp_patient.csv',delim=',')
        getcasecontrol(self, rows, fields)
        
    #%% Get the number of journal lines per patient in a set period of time
    # Period of time is 0 to -1 month, -1 to -2 month, -2 to -3 month and -3 to begin month
    
    def getnumjournallines(self):

        getjournallines(self)
        
    #%% Get attributes per measurement (medication, icpc codes, etc)
    
    def getattributes(self):

        for attr in self.to_process:
            rows, fields = import_data(self.in_dir + '\\gp_' + attr + '.csv', delim=self.delim)
            get_attributes(self, rows, fields, attr)
    
    #%% Combine patterns in the same timeframe (month)
    
    def divideintervals(self):
        divideIntervals(self)
            
    #%% Prep data for saving
    
    def prepforSave(self):
        move_target_to_end_of_list(self)
        self.headers.append('target')
        
    #%% Sort sequences

    def sortsequences(self):
        self.id2data = sort_sequences(self.id2data)
        
    #%% Make the lab values in relative values
    
    def trendfromlabs(self,pfactor=0.1):
        maketrendsfromlab(self, pfactor)
    
    
    #%% Get continuous medication and set to first value
        
    def getcontinuousmed(self):
        getContinuousMed(self)
        
    #%% Create pattern DF (finds patterns and subsequently fills an df)
    
    def patternDF(self):
        if os.path.exists(self.out_dir + '\\patternData\\' + self.trendname):
            gen_pat = False
        else:
            gen_pat = True
        self.df = makePattern(self, self.out_dir + '\\patternData\\' + self.trendname, pattern_cutoff = 0.1, gen_pat = gen_pat)
        
    #%% Save data
    
    def savedata(self):
        if self.baseline==True:
            save_output(self,name=self.name, sub_dir='processedData', headers=self.headers, out_dir = self.out_dir)
        else:
            self.df.reset_index(level=0, inplace = True)
            self.df.rename(columns = {'index':'ID'}, inplace = True)
            self.df.to_csv(self.out_dir + '\\processedData\\' + self.name + '.csv', index = False)
        

def preprocess_pattern(icpc, in_dir, out_dir,numextra, interval, name, trendname, kind_lab = 'base', n_section=12, baseline=True, saveData = False, to_process =  ['episodes', 'medication', 'examination','chronic']):
    # This function creates the class and subsequently does the right processes
    if baseline==True:
        kind_lab = 'base'
    a = preProcessing(icpc, in_dir, out_dir,numextra, interval, name, trendname, kind_lab, n_section, baseline, to_process)
    a.getid()
    a.getocc()
    a.getint()
    a.getcasesandcontrols()
    
    if a.baseline==True:
        a.getnumjournallines()
        
    a.getattributes()
    a.prepforSave()

    if a.baseline==False:
        a.sortsequences()
        if (kind_lab=='rel_ref') and ('examination' in a.to_process):
            a.trendfromlabs(pfactor=0.20)
        if 'medication' in a.to_process:
            a.getcontinuousmed()
        a.sortsequences()
        a.divideintervals()
        a.patternDF()

    if saveData == True:
        a.savedata()
        
    
    