from datetime import date,timedelta
import random

class PatientInterval():
    # Contains the functions to generate random or non-random patient intervals

    def __init__(self,seed):
        # init object by setting the random seed
        random.seed(seed)


    def randomize(self,patient_begin, patient_end, interval):
        # Generate a random patient interval between the un- and registration dates.
        # Additionally, minimum begin and maximum end is specified (has to be between 2012 and 2019)
        # Interval length is selected beforehand. If no interval can be selected, return False (patient will be removed)
        
        # Specify minimum begin and maximum end
        fixed_begin = date(2012, 1, 1)
        fixed_end = date(2019, 12, 31)
        
        # Specify the begin and end measurement days as given by interval
        begin_measurement = timedelta(days=interval[1])
        end_measurement = timedelta(days=interval[0])

        # The latest of the minimum begin and patient begin is the earliest starting point
        min_begin = max(patient_begin, fixed_begin)
        
        # The earliest of the maximum end and the patient end is the latest starting point
        max_begin = min(patient_end, fixed_end) - begin_measurement

        if min_begin > max_begin: # data in the specified interval is not available
            return False
        
        # Choose random day in the possible interval - length of the interval to select
        choose_from = max_begin - min_begin    
        random_day = timedelta(days=int(random.random()*(choose_from.days+1)))
        
        # Add the random day to the minimum begin and subsequently add the interval length
        # This gives a random begin and end within the interval window 
        begin = min_begin + random_day
        end = begin + (begin_measurement-end_measurement)
        
        # Return the random selected begin and end
        return begin, end

    
    def calculate(self,enrollment, dis_diagnosis_date, end_data, interval):
        # Generates a patient interval based on diagnosis date and interval
        # Similar to randomize, but without randomness
        
        # Specify minimum begin
        fixed_begin = date(2012, 1, 1)
        
        # Initialize one day (has to be substracted from the diagnosis date)
        one_day = timedelta(days=1)
        
        # Specify the begin and end measurement days as given by interval
        begin_measurement = timedelta(days=interval[1])
        end_measurement = timedelta(days=interval[0])
        
        # The beginning of the interval is the diagnosis date - interval length - one day
        begin = dis_diagnosis_date - begin_measurement - one_day
        
        # The latest of the minimum begin and the registration date is the earliest data point
        min_begin = max(enrollment, fixed_begin)
        
        # If the earlierst data point is later than the start of the interval, it is not possible to select the whole interval.
        # Therefore, False is returned which removes the patient later on
        if min_begin > begin:
            return False
        
        # Similar: If the interval end is later than the end of the data, the interval cant be selected
        if (dis_diagnosis_date - end_measurement - one_day) > end_data:
            return False
        
        # Return the begin of the interval and the end of the interval
        return begin, (dis_diagnosis_date - end_measurement - one_day)


def insert_data_intervals(info):
    # Selects per patients the interval for which data is used.
    # This is based on the diagnosis date, interval and (un)registration dates
    # Algorithm updates the existing overarching id2data with begin and end interval in the dates list
    
    print ('...getting all patient intervals to be used in the learning process')
    
    # Initialize class and empty list
    patient_interval = PatientInterval(10000)
    to_remove = []
    
    # iterate over dictionary consisting of patients (key) with data (d)
    for key, d in info.id2data.items():
        
        # Select the patient dates
        date_info = d['dis_dates']

        # if the patient is no case ('negative'), randomize an interval between the (un)registration dates. 
        # Else, pick exact the interval selected based on diagnosis date (if possible)
        if date_info[0] == 'negative':
            result = patient_interval.randomize(date_info[1], date_info[2], info.interval)
        else:
            result = patient_interval.calculate(date_info[1], date_info[0], date_info[2], info.interval)
        
        # Add the interval to the date info of the patient
        # If no interval could be selected, set the patient up for removal
        if result:
            date_info.append(result[0])
            date_info.append(result[1])
        else: 
            to_remove.append(key)

    # Remove all keys in the dict for which an interval could not be generated
    for key in to_remove:
        del info.id2data[key]
    
    # Age is stored as birthyear: Set age to acutal age in years
    # If a patient is less old than the minimum age, set up for removal
    to_remove = []
    for key, d in info.id2data.items():
        info.id2data[key]['data'][2] = info.id2data[key]['dis_dates'][3].year-info.id2data[key]['data'][2]
        
        if info.id2data[key]['data'][2] < info.minAge:
            to_remove.append(key)
    
    # Remove the selected patients less than the minimum age
    for key in to_remove:
        if key in info.id2data.keys():
            del info.id2data[key]
        
        