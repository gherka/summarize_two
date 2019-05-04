from PIL import Image
from collections import deque
import numpy as np
import os.path
import pandas as pd

def transform_frequencies(df1, df2, var_name):
    '''
    Adds zero frequency to a variable that is present in one DF, but missing from another.
    '''

    freq_1 = df1[var_name].value_counts()
    freq_2 = df2[var_name].value_counts()

    all_vars = set([var for var in list(df1[var_name].unique()) + list(df2[var_name].unique())])

    new_freq_1 = []
    new_freq_2 = []

    for var in all_vars:
        if var in freq_1:
            new_freq_1.append([var, freq_1[var]])
        else:
            new_freq_1.append([var, 0])
        
        if var in freq_2:
            new_freq_2.append([var, freq_2[var]])
        else:
            new_freq_2.append([var, 0])

    bar_1 = np.array(new_freq_1, dtype=object).T
    bar_2 = np.array(new_freq_2, dtype=object).T

    return(bar_1, bar_2)

def read_data(data_path_1, data_path_2):
    '''
    Currently, only .csv and Excel files are supported.
    Possible to bring more, as long as they integrate into Pandas
    Filename is written into _metadata attribute of each dataframe.
    Watch out for version updates as work is underway to change
    how metadata is stored and propagated in dataframes
    '''

    #Read the first dataset
    if os.path.splitext(data_path_1)[1] == '.csv':

        df1 = pd.read_csv(data_path_1)
        df1._metadata = {'file_name':os.path.basename(data_path_1)}

    elif os.path.splitext(data_path_1)[1] in ['.xlsx', '.xls']:

        df1 = pd.read_excel(data_path_1)
        df1._metadata = {'file_name':os.path.basename(data_path_1)}

    #Read the second dataset
    if os.path.splitext(data_path_2)[1] == '.csv':

        df2 = pd.read_csv(data_path_2)
        df2._metadata = {'file_name':os.path.basename(data_path_2)}

    elif os.path.splitext(data_path_2)[1] in ['.xlsx', '.xls']:

        df2 = pd.read_excel(data_path_2)
        df2._metadata = {'file_name':os.path.basename(data_path_2)}

    return df1, df2

def dtype_mapping(input_key, reverse=False):
    '''
    Performs conversion between Pandas inferred data types and user-generated ones
    Returns mapped value given an input key; parse_dates is a magic value
    '''
    
    dtype_map = {'object':'Categorical', 'int':'Continuous', 'float':'Continuous', 'datetime':'Timeseries'}
    dtype_map_reverse = {'Categorical':'object', 'Continuous':'float64', 'Timeseries':'parse_dates'}
    
    if reverse:
        return dtype_map_reverse[input_key]
            
    for mapping_key in dtype_map.keys():
        if mapping_key in str(input_key):
            return dtype_map[mapping_key]
        
    return 'unknown'