import os
import csv

def make_dir(s):
    '''creates the directory s if it does not exist'''
    if not os.path.exists(os.path.dirname(s)):
        os.makedirs(os.path.dirname(s)) 

def write_csv(f):
    '''opens a csv writer object'''    
    return csv.writer(open(f,"w", newline=''))

def save_output(info,benchmark=False, sequence_file=False, sub_dir='', name='unnamed', target=False, headers = [], out_dir=[]):
    '''saves processed data to the specified output directory'''
    print('...saving processed data')# to {}'.format('sql' if self.from_sql else 'file')

    # possibly make new directories
    out_dir = out_dir + '//' + sub_dir + '//'
    make_dir(out_dir)

    f_out = out_dir + name + '.csv'
    out = write_csv(f_out)
    
    out.writerow(headers)
    
    for value in info.id2data.values():
        data = value['data']
        data[2] = 1 if data[2] == 'V' else 0
        data[-1] = 0 if data[-1] == 'negative' else 1
        
        out.writerow(data)
    