import random

class SelectCasesControls():
    
    def __init__(self,seed,info):
        '''init object by setting the random seed'''
        random.seed(seed)
        self.info = info
        
    def getIDcasescontrols(self):
        # Select the index of both cases and controls, and save them in this class
        self.cases = []
        self.controls = []
        
        # Select cases and controls indices
        for key, d in self.info.id2data.items():
            if d['dis_dates'][0]!='negative':
                self.cases.append(key)
            else:
                self.controls.append(key)
        
    def findPrak(self, pat):
        # Identify the pracnumber from a patient ID
        for key in self.prak:
            if pat in self.prak[key]:
                return key  
            
    def getPatinPrak(self, rows, fields):
        # Identify in which practice a patient is (for matching per prac)
        # Return a dict with per prac id a list of patient ids
        self.prak=dict()
        
        prak_idx = fields.index('gp_praknr')
        pat_idx = fields.index('gp_patidf')
        
        for row in rows:
        
            if int(row[prak_idx]) in self.prak:
                if int(row[pat_idx]) in self.prak[int(row[prak_idx])]:
                    continue
                else:
                    self.prak[int(row[prak_idx])] = self.prak[int(row[prak_idx])] + [int(row[pat_idx])]
            else:
                self.prak[int(row[prak_idx])] = [int(row[pat_idx])]
    
    def findControlinPrak(self, caseInfo, prakpats, id2data, matchagesex, listneg, numControls):
        # Find the controls in a practice, based on equal age and sex if desired (not used in original article)
        equalSex = []
        equalAge = []
        
        if matchagesex == False:
            # Find controls who are controls (listneg) and are in a prac (prakpats)
            p = set(prakpats)
            n = set(listneg)
            equalSex = list(n.intersection(p))
            return equalSex
        
        # From below here, this is optionel (not used)
        for pat in prakpats:
            try:
                
                if (id2data[pat]['data'][3] == caseInfo['data'][3]) and (id2data[pat]['data'][0]=='negative'):
                    equalSex.append(pat)
            except:
                continue
            
        if not equalSex:
            return equalAge
        
        for pat in equalSex:
            try:
                
                if id2data[pat]['data'][2] == caseInfo['data'][2]:
                    equalAge.append(pat)
            except:
                continue
            
        if len(equalAge) < numControls:
            for pat in equalSex:
                try:
                    
                    if (id2data[pat]['data'][2] <= caseInfo['data'][2]+5) or (id2data[pat]['data'][2] >= caseInfo['data'][2]-5):
                        equalAge.append(pat)
                except:
                    continue
        
        return equalAge
    
    def getControls(self, matchAgeSex, numControls):
        # Select controls for each case
        self.select_control = []
        self.noControl=[]
        
        # Create a list of all controls
        allControls = [x for x in self.info.id2data if self.info.id2data[x]['data'][0]=='negative']
        
        # For each case, find the pracnumber and subsequently the controls in that practice
        # Select the controls which are not yet selected (include each control only once)
        # If the desired number of controls is found, save these
        countcase = 0
        for case in self.cases:
            countcase += 1
            praknr = self.findPrak(case)
            controlList = self.findControlinPrak(self.info.id2data[case], self.prak[praknr], self.info.id2data, matchAgeSex, allControls, numControls)
            possible_controls = [x for x in controlList if x not in self.select_control]
            if len(possible_controls) < numControls:
                self.noControl.append(case)
                continue
            self.select_control.extend(random.sample(possible_controls, k=numControls))
        


def getcasecontrol(info, rows, fields):
    # Select cases and controls
    print('Select cases and controls')

    casecontrols = SelectCasesControls(10000,info)
    
    # Get the ID for cases and controls
    casecontrols.getIDcasescontrols()
    
    # If extra samples are wanted, select an x number of controls (no cases)
    if info.NumExtraSamples > 0:
        try:
            randsamp = random.sample(casecontrols.controls, len(casecontrols.cases)*info.NumExtraSamples)
        except:
            randsamp = random.sample(casecontrols.controls, len(casecontrols.controls))
            
        controlid2data = {x:info.id2data[x] for x in randsamp}
        info.id2data = controlid2data
        return 
    
    # If no extra samples are wanted, select cases and controls
    # Identify in which practice a patient is (for matching per prac)
    casecontrols.getPatinPrak(rows, fields)
    
    # Select controls for each case based on the same clinic
    casecontrols.getControls(info.matchAgeSex, info.numControls)
    
    print('Number of no controls: {}'.format(len(casecontrols.noControl)))
    
    # Save data
    caseid2data = {x:info.id2data[x] for x in casecontrols.cases if x not in casecontrols.noControl}
    controlid2data = {x:info.id2data[x] for x in casecontrols.select_control}

    id2data_temp = controlid2data.copy()
    id2data_temp.update(caseid2data)
    
    info.id2data = id2data_temp
    