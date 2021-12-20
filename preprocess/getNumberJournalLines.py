from dateutil.relativedelta import relativedelta
import pickle

def getjournallines(info):
    # Get the number of journallines in the 0-1, 1-2, 2-3 and 3-12 months before end of time.

    print('...Selecting number of journal lines')
    
    f= open(info.in_dir + '\\gp_journaldata', 'rb')
    journaldata = pickle.load(f)
    f.close()
    
    for pat in info.id2data.keys():
        try:
            t1 = len([x for x in journaldata[pat] if x > info.id2data[pat]['dis_dates'][4] + relativedelta(months=-1)
                      and x < info.id2data[pat]['dis_dates'][4]])
            t2 = len([x for x in journaldata[pat] if x > info.id2data[pat]['dis_dates'][4] + relativedelta(months=-2)
                      and x <= info.id2data[pat]['dis_dates'][4] + relativedelta(months=-1)])
            t3 = len([x for x in journaldata[pat] if x > info.id2data[pat]['dis_dates'][4] + relativedelta(months=-3)
                      and x <= info.id2data[pat]['dis_dates'][4] + relativedelta(months=-2)])
            t4 = len([x for x in journaldata[pat] if x > info.id2data[pat]['dis_dates'][3]
                      and x <= info.id2data[pat]['dis_dates'][4] + relativedelta(months=-3)])
        except:
            t1 = 0
            t2 = 0
            t3 = 0
            t4 = 0
            
        info.id2data[pat]['data'].extend([t1,t2,t3,t4])
        
    info.headers = info.headers + ['oneMonthCount', 'twoMonthCount','threeMonthCount','beginDataCount']