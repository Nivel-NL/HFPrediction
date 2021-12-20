from .convertPatientFile import getGoodPrak, convertPatient
from .io_data import import_data
from .convertMedication import convertMedicationData
from .convertExamination import processUitslagenFiles
from .convertIcpc import convertICPCdata
from .convertICPCtoCounts import convertICPCCounts

class convertData():
    # Convert raw data into csv files which can be preprocessed and be used for feature extraction
    # Class consist of numerous functions, which except from ICPCcounts can be processed seperately.
    
    def __init__(self, ICPCcode, in_dir, out_dir):
        self.in_dir = in_dir
        self.delim = ','
        self.out_dir = out_dir
        self.ID_column = 'randompatnr'
        self.ICPCcode = ICPCcode
        

    def convertpatient(self):
        # Select which GP practices can be used for analysis based on amount and quality of data.
        # Subsequently, save demographics and (un)registration dates per patient
        
        print('...Converting patient files')
        rows, fields = import_data(self.in_dir + '\\Praktijk.csv')
        good_prak = getGoodPrak(rows, fields)
        
        rows, fields = import_data(self.in_dir + '\\Patient.csv')
        convertPatient(rows, fields, good_prak ,self.out_dir + '\\gp_patient.csv')
        

    def convertmedication(self):
        # Convert raw medication files to a format used for preprocessing.
        # This puts dates in one format, and sets atc codes at a length of 5
        
        print('...Converting medication files')
        rows, fields = import_data(self.in_dir + '\\Prescriptie.csv')
        convertMedicationData(rows, fields, self.out_dir + '\\gp_medication.csv')
        

    def convertexamination(self):
        # Convert raw examination files to a standard format for preprocessing.
        # In addition, save the value based on the type of examination and correct errors.
        
        print('...Converting diagnostic files')
        processUitslagenFiles(self.in_dir, self.out_dir + '\\gp_examination.csv', manual_check = False)


    def convertICPC(self):
        # Convert icpc files to a standard format for processing.
        # The icpc target code should be selected from the chronic diseases.
        # Therefore, First only save icpc codes from the journal without icpc target code.
        # Second, only save icpc codes from the chronic file with icpc target code
        
        print('...Converting ICPC files')
        rows, fields = import_data(self.in_dir + '\\Journaal.csv')
        convertICPCdata(rows, fields, self.ICPCcode, True, self.out_dir + '\\gp_episodes.csv', self.in_dir)

        rows, fields = import_data(self.in_dir + '\\Episode.csv')
        convertICPCdata(rows, fields, self.ICPCcode, False, self.out_dir + '\\gp_episodes.csv', self.in_dir)
        

    def convertChronicICPC(self):
        # Similar to convertICPC
        # Convert chronic icpc files to a standard format for processing.
        # Codes corresponding to the icpc target code are removed
        
        print('...Converting chronic ICPC files')
        rows, fields = import_data(self.in_dir + '\\Episode.csv')
        convertICPCdata(rows, fields, 'Chronic', True, self.out_dir + '\\gp_chronic.csv', self.in_dir)
        

    def convertICPCcounts(self):
        # Get the unique dates on which a patient has a ICPC code for counting in the preprocessing
        print('...Converting counting patient files')
        rows, fields = import_data(self.out_dir + '\\gp_episodes.csv')
        convertICPCCounts(rows, fields, self.out_dir)