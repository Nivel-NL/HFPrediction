from datetime import date, datetime

def monthToNum(shortMonth):
    '''convert month name (3 letters) to the month number'''
    return {
            'jan' : 1,
            'feb' : 2,
            'mar' : 3,
            'apr' : 4,
            'may' : 5,
            'jun' : 6,
            'jul' : 7,
            'aug' : 8,
            'sep' : 9, 
            'oct' : 10,
            'nov' : 11,
            'dec' : 12
    }[shortMonth]

def str2date(date_str, ymd=True, yy=False, give_default_begin=False, give_default_end=False):
    '''converts strings with a date to datetime dates (yyyy-mm-dd)'''
    # This function is altered so it can handle dates like 07oct1967
    if type(date_str) == date:
        return date_str 

    if type(date_str) == datetime:
        return date_str.date()

    if date_str == None or (type(date_str) == str and date_str.strip() == ''):
        if give_default_begin:
            return str2date("1850-01-01")
        elif give_default_end:
            return str2date("2050-12-31")
        else:
            print('str2date encountered a value "{}" of type "{}" which it cannot handle'.format(date_str, type(date_str)))
            return -1
    
    date_pre = date_str.replace(' ','-')
    date_lst = date_pre.split('-')
    if yy:
        year = date_lst[2]
        year = '20'+year if int(year) < 70 else '19'+year
        return date(int(year), int(date_lst[1]), int(date_lst[0]))
    if ymd: # regular ymd format
        return date(int(date_lst[0]), int(date_lst[1]), int(date_lst[2]))
    if not ymd: # unenrollment dmy format
        try:
            return date(int(date_lst[2]), int(date_lst[1]), int(date_lst[0]))
        except:
            return date(int(date_lst[0][5:9]), monthToNum(date_lst[0][2:5]), int(date_lst[0][0:2]))
        
def convertCodeToICPC(numcode):
    '''converts icpc numeric codes to alphabetic codes'''
    convert_dict = {10:'A', 11:'B', 12:'D', 13:'F', 14:'H', 15:'K',16:'L', 17:'N', 18:'P', 19:'R', 20:'S', 21:'T',
                22:'U',23:'W',24:'X',25:'Y',26:'Z'}
    try:
        return convert_dict[int(numcode[0:2])] + numcode[2:4]
    except:
        return 'Q00'