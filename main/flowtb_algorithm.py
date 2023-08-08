import os 
import pandas as pd
from itertools import combinations

def preprocessing(filename, number=1):
    '''Return processed dataframe'''
    
    # define 'for_process' sequence
    processes = ['Sourcing', 'Conditioning', 'Treatment', 'Forwarding', 'Delivery']
    # read an excel file
    df = pd.read_excel(filename, sheet_name='Input' + str(number))
    # delete irrelevant columns, i.e., ['product', 'treatment']
    df = df.drop(df.columns[[0, 1]], axis=1)
    # convert 'for_process' to number
    df['for_process'] = df['for_process'].apply(lambda x: processes.index(x))
    # sort 'Week', 'for_process'
    df = df.sort_values(by=['Week', 'for_process'], ignore_index=True)
    # round amount to 2 decimal places
    df['Amount'] = df['Amount'].apply(lambda x: round(x, 2))
    return df

def group_indices(indices):
    '''Group Indices within same path'''
    
    index_groups = []
    for idx, sub_idx in sorted(indices):
        if len(index_groups) == 0 or index_groups[-1][0][0] != idx:
            index_groups.append([(idx, sub_idx)])
        else:
            index_groups[-1].append((idx, sub_idx))
    return index_groups

def retrive_cache(sub_path):
    '''Retrive cache amount of sub-path, and reset cache'''
    
    if sub_path['cache']:
        sub_path['amount'][0] = sub_path['cache']
        sub_path['cache'] = None
        
def rearrange_subpaths(paths, group):
    '''Rearrange separable subpaths s.t. they stick together'''
    
    assert len(set([idx for idx, _ in group])) == 1, 'invalid indices in group!'
    path = paths[group[0][0]]
    first_sub_idx = group[0][1]
    sub_paths_temp = []
    sub_idxs = sorted([sub_idx for _, sub_idx in group[1:]], reverse=True)
    for sub_idx in sub_idxs:
        sub_paths_temp.append(path.pop(sub_idx))
    path[first_sub_idx+1:first_sub_idx+1] = sub_paths_temp

def update_path(paths, indices, df_row, separable=True):
    '''Update current paths using df_row'''
    
    if df_row['for_process'] == 4:  # case I: initialize new path
        paths.append([{'process': [4],
                       'amount': [df_row['Amount']],
                       'week': [df_row['Week']],
                       'country': [df_row['send_from_cnt'], df_row['to_processing_cnt']],
                       'trace': [df_row.name],
                       'cache': None}
                      ])
    elif separable:  # case II: old path is separable
        groups = group_indices(indices)
        for group in groups:
            total_amount = 0
            for idx, sub_idx in reversed(group[1:]):
                # update non-first sub-paths (putting None)
                sub_path = paths[idx][sub_idx]
                total_amount += sub_path['amount'][0]
                retrive_cache(sub_path)
                sub_path['country'][0] = None
                for string in ['process', 'amount', 'week', 'country', 'trace']:
                    sub_path[string].insert(0, None)
            # update first sub-path
            first_sub_path = paths[group[0][0]][group[0][1]]
            total_amount += first_sub_path['amount'][0]
            retrive_cache(first_sub_path)
            first_sub_path['process'].insert(0, df_row['for_process'])
            first_sub_path['amount'].insert(0, total_amount)
            first_sub_path['week'].insert(0, df_row['Week'])
            first_sub_path['country'].insert(0, df_row['send_from_cnt'])
            first_sub_path['trace'].insert(0, df_row.name)
            # Rearrange subpaths
            rearrange_subpaths(paths, group)
    else:  # case III: old path is not separable, i.e., initialize new sub-path
        assert len(indices) == 1, 'indices must contain only a pair (idx, sub-idx)!'
        idx, sub_idx = indices[0]
        sub_path = paths[idx][sub_idx]
        # # update old sub-path (need to modify amount later!!)
        # new_amount = round(sub_path['amount'][0] - df_row['Amount'], 2)
        # sub_path['amount'][0] = new_amount
        
        # cache amount of old sub-path
        if sub_path['cache'] is None: sub_path['cache'] = sub_path['amount'][0]
        sub_path['amount'][0] = round(sub_path['amount'][0] - df_row['Amount'], 2)
        # initialize new sub-path
        null = [None] * len(sub_path['amount'])
        paths[idx].insert(sub_idx + 1, 
                          {'process': [df_row['for_process']] + null,
                           'amount': [df_row['Amount']] + null,
                           'week': [df_row['Week']] + null,
                           'country': [df_row['send_from_cnt']] + [df_row['to_processing_cnt']] + null,
                           'trace': [df_row.name] + null,
                           'cache': None})
        
def check_valid_paths(paths, df_row):
    '''Return path indices that have valid country and process, and total demand amount'''
    
    # format: [(idx0, sub_idx0), (idx1, sub_idx1), ...]
    valid_path_indices = []
    total_amount = 0
    for idx, path in enumerate(paths):
        for sub_idx, sub_path in enumerate(path):
            if (df_row['to_processing_cnt'] == sub_path['country'][0] and 
                df_row['for_process'] < sub_path['process'][0]):
                valid_path_indices.append((idx, sub_idx))
                total_amount += sub_path['amount'][0]
    return valid_path_indices, round(total_amount, 2)

def is_saparable(paths, indices, target_amount, debugging=False):
    '''Return path indices s.t. sum of their amounts equals target_amount'''
    
    # get path indices s.t. amount <= order_amount
    amounts = [(idx, sub_idx, paths[idx][sub_idx]['amount'][0]) 
               for (idx, sub_idx) in indices 
               if paths[idx][sub_idx]['amount'][0] <= target_amount]
    if debugging: print('amounts:', amounts)
    
    # find exact separable demands, e.g., order_amount = demand1 + demand3
    for k in range(1, len(amounts) + 1):
        for comb in combinations(amounts, k):
            amounts_sum = round(sum([item[-1] for item in comb]), 2)
            if target_amount == amounts_sum:
                return True, [(item[0], item[1]) for item in comb]
    return False, []
        
def select_best_path(paths, indices, df_row):
    '''Return best path assuming amount of df_row is not separable
    best path: path demanding more amount than df_row'''
    
    max_amount = 0
    max_index = 0
    for i, (idx, sub_idx) in enumerate(indices):
        amount = paths[idx][sub_idx]['amount'][0]
        if amount > max_amount:
            max_amount = amount
            max_index = i
    return [indices[max_index]]

def traceback(paths, df_row, debugging=False):
    '''Traceback some paths using df_row'''
    
    # get valid paths for current df_row
    valid_path_indices, total_amount = check_valid_paths(paths, df_row)
    if debugging:
        print('Total demand amount {}; Valid path indices: {}'
              .format(total_amount, valid_path_indices))
    # if no valid paths, skip this df_row
    if len(valid_path_indices) == 0:
        if debugging: print('no valid paths!')
        return
    
    # decide how to separate amount of df_row
    if df_row['Amount'] == total_amount:  
        update_path(paths, valid_path_indices, df_row)
    elif df_row['Amount'] < total_amount:
        separable, indices = is_saparable(paths, valid_path_indices, 
                                          df_row['Amount'], debugging)
        if separable:
            update_path(paths, indices, df_row)
        else:  # df_row amount is not separable
            indices = select_best_path(paths, valid_path_indices, df_row)
            update_path(paths, indices, df_row, False)
    else:  # if amount of df_row > total_amount, skip this df_row (no valid paths)
        if debugging: print('order amount exceeds total amount!')
        
def show_df_row(df_row):
    '''[Debugging] Show information of df_row'''
    
    origin, destination = df_row['send_from_cnt'], df_row['to_processing_cnt']
    process, amount = df_row['for_process'], df_row['Amount']
    print('row {}: {} -> {}, process {}, amount {}'.format(df_row.name, origin, 
                                                           destination, process, amount))
    
def show_paths(paths):
    '''[Debugging] Show cuurent state of all paths'''
    
    for idx, path in enumerate(paths):
        for sub_idx, sub_path in enumerate(path):
            print('Path {}: amount {}, cnt {}, trace {}'
                  .format((idx, sub_idx), sub_path['amount'], sub_path['country'], 
                          sub_path['trace']))

def postprocessing(paths):
    '''Put sub-paths into desired format'''
    
    # construct results containing paths with desired format
    results = []
    processes = ['Sourcing', 'Conditioning', 'Treatment', 'Forwarding', 'Delivery']
    for idx, path in enumerate(reversed(paths)):
        for sub_idx, sub_path in enumerate(path):
            # augment sub-path
            augment_len = len(processes) - len(sub_path['process'])
            for name in ['process', 'amount', 'week', 'country', 'trace']:
                sub_path[name] = [None] * augment_len + sub_path[name] 
            
            # construct result sub-path
            result = []
            for i in range(len(processes)):
                process_idx = sub_path['process'][i]
                process_name = processes[process_idx] if process_idx is not None else None
                result += [process_name, sub_path['country'][i+1],
                           sub_path['week'][i], sub_path['amount'][i]]
            demand = str(idx + 1) 
            if len(path) > 1: demand += '--' + str(sub_idx + 1)
            result.append(demand)
            results.append(result)
    return results

def color_path(df_row):
    '''Color path in dataframe'''
    
    colors = ['#FFE4C4', '#7FFFD4', '#98F5FF', '#FF9912', '#76EE00', 
              '#6495ED', '#CAFF70', '#BF3EFF', '#97FFFF', '#FF1493',
              '#FFD700', '#FFB6C1', '#AB82FF', '#FA8072', '#FFA54F']
    path_num = int(df_row['Demand'].partition('--')[0])
    bg = 'background-color: {}'.format(colors[(path_num-1) % len(colors)])
    return [''] * (len(df_row) - 5) + [bg] * 5
    
def save_xlsx(results, filename='NetworkFlowProblem-Output.xlsx', number=1, debugging=False):
    '''Save results into excel file'''
    
    # construct column names and color dataframe
    columns = [['Process' + str(i), 'Cnt' + str(i), 'Week' + str(i), 'Amount' + str(i)] 
               for i in range(1, 6)]
    columns = sum(columns, []) + ['Demand']
    df_results = pd.DataFrame(results, columns=columns)
    df_results = df_results.style.apply(color_path, axis=1)
    df_results.highlight_null(color='gainsboro')
    if debugging: print(df_results)
    # save dataframe into excel file
    if os.path.exists(filename):
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', 
                            if_sheet_exists='replace') as writer:  
            df_results.to_excel(writer, sheet_name='Output' + str(number), index=False)
    else:
        with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:  
            df_results.to_excel(writer, sheet_name='Output' + str(number), index=False)

def flow_traceback(filename_input, filename_output='NetworkFlowProblem-Output.xlsx', 
                   number=1, debugging=False):
    '''[Main function] Read network flow info, traceback flow, and save to excel file'''
    
    df = preprocessing(filename_input, number)
    if debugging: print(df)
    paths = list()
    for row in range(len(df.index)-1, -1, -1):
        df_row = df.iloc[row]
        if debugging: show_df_row(df_row)
        if df_row['for_process'] == 4:
            update_path(paths, None, df_row)
        else:
            traceback(paths, df_row, debugging)
            if debugging: show_paths(paths)
        if debugging: print()
    results = postprocessing(paths)
    save_xlsx(results, filename_output, number)
