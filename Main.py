#%% Import the necessary underlying code

from Convertdata.convertStart import convertData
from preprocess.preprocessData import preprocess_pattern
from Learning.MainLearning import collectData

#%% Initialize parameters

# ICPC code to investigate
icpc_code = 'K77'

# Conversion in and out directiories
# For publication, the main folder is removed
main_folder = 'C:\\ThisIsTheMainFolder\\'
conv_indir = main_folder + 'Raw'
conv_outdir = main_folder + 'convertedData'

# Processing in and out directories
proc_indir = main_folder + 'convertedData'
proc_outdir = main_folder + 'processedData'

# Training set contruction directories
trainset_indir = main_folder + 'processedData\\processedData'
trainset_outdir = main_folder + 'processedData\\dataForTraining'

# Interval in days where data is selected [-closest to diagnosis, -furthest]
interval = [int(365+1), int(730+1)]

#%% Conversion of raw data in data which can be processed
# Intermediate steps can be selected for time purposes
# Activate when needed

conversion = convertData(icpc_code, conv_indir, conv_outdir)
conversion.convertpatient()
conversion.convertmedication()
conversion.convertexamination()
conversion.convertICPC()
conversion.convertChronicICPC()
conversion.convertICPCcounts()

#%% Processing of converted data into a format suitable for machine learning
# Furthermore, here is where cases are identified and parameters are extracted

# Baseline and numExtraPat can be altered, to create seperate datasets.
# Baseline = True creates the presence of codes, Baseline = False creates trends
# numExtraPat = 0 creates a 1:1 ratio, anything else just includes the controls from a 1:num ratio

for baseline in [True, False]:
    for numExtraPat in [0, 44]:

        saveData = True
        
        if baseline == True:
            
            if numExtraPat == 0:
                nameDataFile = 'Baseline_12month'
            else:
                nameDataFile = 'BaselineExtraPatients_12month'
        else:
            
            if numExtraPat == 0:
                nameDataFile = 'Trend_12month'
            else:
                nameDataFile = 'TrendExtraPatients_12month'
        
        preprocess_pattern(icpc_code, proc_indir, proc_outdir,
                               numExtraPat, interval,
                               nameDataFile,
                               'Trend_12month',
                               kind_lab='rel_ref',
                               n_section=12,
                               baseline=baseline,
                               saveData = saveData,
                               )

#%% Creating the training set for machine learning in 1 file

# We select which dataset(s) to use, and if these should be saved for machine learning next.
# If we don't save them, select just 1 set, if you would like to save them, you can select a list

toSaveData = True
dataset = [1,2,3,4,5,6]
trainmod = collectData('12', dataset, toSaveData, trainset_indir, trainset_outdir)


#%% Model training and testing
# Model training is (for now) performed in separate scripts in JupyterLab
# Model training: Training algorithm.ipynb
# Model testing and plotting: PlotCurves.ipynb
