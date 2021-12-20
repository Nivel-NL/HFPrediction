import numpy as np
from collections import defaultdict
from .StateInterval import StateInterval
from .StateSequence import StateSequence
from .Pattern import Pattern, enrich_pattern
import pickle
from scipy.stats import fisher_exact
from scipy.stats import chi2_contingency

def patients_with_class_val(arr, class_val):
    result = {lst[0] : lst[1:-1] for lst in arr if lst[-1] == class_val}
    for k in result:
        record = result[k][2:]
        gender = result[k][1]
        birthyear = result[k][0]
        for i in range(len(record)):
            if type(record[i]) != StateInterval:
                str_SI = record[i].split(';')
                record[i] = StateInterval(str_SI[0], str_SI[1], str_SI[2])
        result[k] = StateSequence(record, k, gender, birthyear)
    return result

def generate_F1(data_dict, min_sup, negated_data):
    len_data = len(data_dict)

    instances = [data_dict[sequence].get_states() for sequence in data_dict ]

    y_occurrences = defaultdict(int)
    for states in instances:
        for state in set(states): # for all unique states
            y_occurrences[state] += 1

    negated_instances = [negated_data[sequence].get_states() for sequence in negated_data ]
    all_occurrences = dict(y_occurrences)
    for states in negated_instances:
        for state in set(states): # for all unique states
            if state not in all_occurrences:
                all_occurrences[state] = 0
            all_occurrences[state] += 1

    # calc frequent patterns (more freq than min_sup)
    init_mcs = len_data / len_data + len(negated_data)
    # init_mc = len(data_dict) / (len(data_dict) + len(negated_data))

    F1=dict()
    for key in y_occurrences:
        states = np.array([key])
        relations = np.empty((1,1), dtype='S1')
        relations.fill(' ')
        loc_support = y_occurrences[key]/float(len_data)
        y_support = y_occurrences[key]/float(len_data+len(negated_data))
        all_support = all_occurrences[key]/float(len_data+len(negated_data))
        if loc_support >= min_sup:
            F1[key] = Pattern(states, relations, sup=loc_support, subpatterns=[], in_candidates=True)
            F1[key].generate_id_list(data_dict, False)
            F1[key].generate_id_list(negated_data, True)
            F1[key].is_frequent = (loc_support >= min_sup)
            F1[key].mcs = init_mcs
            F1[key].confidence = y_support/float(all_support)
            F1[key].calc_max_conf()
    return F1

def generate_coherent_superpatterns(P, S, data_dict, all_patterns, strict_matching=True):

    superpatterns = []
    rel_length = P.relations.shape[1] + 1
    rels = np.empty((rel_length), dtype='S1')
    rels.fill('b')
    rels[0] = ' '

    new_p = enrich_pattern(P, S, rels, data_dict)
    if new_p not in all_patterns:
        superpatterns.append(new_p)
        all_patterns.append(new_p)
        
    if strict_matching:
        for i in range(1, len(rels)):

            '''# semantic abstraction compatibility check
            # if not compatible, adding another 'c' will never make it compatible
            # so we safely return!
            if not compatible(P.states[i-1], S.states[0]): 
                return superpatterns, all_patterns'''

            rels[i] = 'c'
            new_p = enrich_pattern(P, S, rels, data_dict)
            if new_p not in all_patterns:
                superpatterns.append(new_p)
                all_patterns.append(new_p)

    return superpatterns, all_patterns

def generate_candidates(all_patterns, Fk, F1, min_sup, data_dict):

    # Fk_singletons = set()
    # for fp1 in F1:
    #     for fpk in Fk:
    #         for state in fpk.states:
    #             if state == fp1.states[0]:
    #                 Fk_singletons.add(fp1)
    Fk_singletons = set(fp1 for fp1 in F1 for fpk in Fk for state in fpk.states if state == fp1.states[0])
    len_data = float((len(data_dict)))

    candidates = []
    for k_pattern in Fk: # for all frequent k-patterns
        for singleton in Fk_singletons: # for all unique singleton states in the current Fk states
            superpatterns, all_patterns = generate_coherent_superpatterns(k_pattern, singleton, data_dict, all_patterns) # generate new candidates

            for superpattern in superpatterns: # for each k+1-pattern created, we check if it is frequent
                subpatterns = superpattern.get_subpatterns()
    
                # intersection of all created subpatterns and all frequent k-patterns 
                frequent_subs = [pattern for pattern in Fk if pattern in subpatterns]

                # if the created subpatterns are all in Fk
                if len(frequent_subs) >= len(subpatterns):
                    if len(frequent_subs) > len(subpatterns):
                        print('> (impossible)')
                    superpattern.generate_pid_list(frequent_subs)
                    superpattern.generate_pid_list(frequent_subs, negated=True) #Nieuw
                    # superpattern.calc_max_conf_subpatterns(frequent_subs)
                    if (len(superpattern.pid_list)/len_data) > min_sup:
                        candidates.append(superpattern)
    return candidates, Fk_singletons

def evaluate_support(patterns, data, min_sup, negated_data, MPTPs):
    len_data = len(data)

    result = []
    p_values = []
    for p in patterns:
        p.generate_id_list(data, negated=False)
        p.generate_id_list(negated_data, negated = True)
        p.calculate_support(min_sup, len_data)
        pvalue = check_significance(p, len(p.pid_list), len(p.pid_list_negated))
        p.pvalue=pvalue
        if p.support >= min_sup:
            result.append(p)

    return result

def check_significance(patroon, lenpos, lenneg):
    
    oddsratio, pvalue = fisher_exact([[len(patroon.id_list), lenpos-len(patroon.id_list)], [len(patroon.id_list_negated), lenneg-len(patroon.id_list_negated)]])
    return pvalue

def mine(data_dict, min_sup, negated_data, verbose):
    print("...generating 1-patterns"),
    F1 = generate_F1(data_dict, min_sup, negated_data)
    
    for patroon in F1.values():
        pv = check_significance(patroon, len(data_dict), len(negated_data))
        patroon.pvalue = pv

    if verbose: print(F1)
    k_max = len(max(data_dict.values(), key=len)) if len(data_dict)!=0 else 0 # k = length of the longest instance, because that is how the maximum number of combinations possible for this specific group
    if verbose: print("longest patient sequence: " + str(k_max))
    
    F1 = set(F1.values())
    new_F1 = F1
    Fk = set(F1)
    MPTPs = set([p for p in F1 if p.is_significant(alpha=0.05)])
    candidates = list(F1)
    print("...found " + str(len(candidates)))
    result = list(candidates)
    
    for k in range(0,k_max):
        print("...generating " + str(k+2) + '-patterns')

        potential_Fk, new_F1 = generate_candidates(candidates, Fk, new_F1, min_sup, data_dict)
        Fk = evaluate_support(potential_Fk, data_dict, min_sup, negated_data, MPTPs)

        result = result + Fk
        print("...found " + str(len(Fk)))
        if len(Fk) == 0:
            break
        if k==1: 
            break
    return result, MPTPs#[c for c in result if c.is_frequent]

def generate(sequence_file, min_sup, verbose=False):
    # Generate patterns: First all 1Patterns with enough support, then all subsequent 2Patterns, etc...
    sequences = (v['data'] for k, v in sequence_file.items())
    sequences_pos = patients_with_class_val(sequences, 'positive')

    sequences = (v['data'] for k, v in sequence_file.items())
    sequences_neg = patients_with_class_val(sequences, 'negative')

    if verbose: 
        print("Patient dict:")
        print(sequences_neg)

    print('###### Mining positive dis freq patterns ######')
    frequent_patterns_pos, MPTP_pos = mine(sequences_pos, min_sup, sequences_neg, verbose)
    
    print('###### Mining negative dis freq patterns ######')
    frequent_patterns_neg, MPTP_neg = mine(sequences_neg, min_sup, sequences_pos, verbose)
    
    print('###### Done mining patterns ######')
    return list(set(frequent_patterns_pos+frequent_patterns_neg)), frequent_patterns_pos, frequent_patterns_neg

