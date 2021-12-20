import csv
from os import path

def read_csv(f, delim=','):
    '''opens a csv reader object'''
    return csv.reader(open(f, 'r'), delimiter=delim)

def get_headers(row):
    '''returns the non-capitalised and bugfixed version of the header'''
    headers = [el.lower() for el in row]
    headers[0] = headers[0].split("\xef\xbb\xbf")[1] if headers[0].startswith('\xef') else headers[0] # fix funny encoding problem
    return headers

def import_data(f, delim=','):
    '''import data and separates the column names from the data'''

    rows = read_csv(f, delim=delim)
    headers = get_headers(next(rows))
    return rows, headers

def write_csv(f):
    '''opens a csv writer object'''    
    return csv.writer(open(f,"w", newline=''))

def dictToCSV(data, header, out_dir):
    '''saves the dict to a csv'''
    sortInd=sorted(data)
    out = write_csv(out_dir + '\\gp_patient.csv')
    out.writerow(header)
    for ind in sortInd:
        out.writerow([ind] + data[ind])
        
def writeDict_csv(f, header,sortopen="a"):
	'''opens a csv writer object'''	
	return csv.DictWriter(open(f,sortopen, newline=''), fieldnames = header)

def dictlistToCSV(data, header, f_out,writeHeader=False):
    '''saves the list with dicts to a csv'''
    if path.exists(f_out) == False:
        out = writeDict_csv(f_out, header, sortopen = "w")
        out.writeheader()

    else:
        out = writeDict_csv(f_out, header)
    
    for dictdata in data:
        out.writerow(dictdata)