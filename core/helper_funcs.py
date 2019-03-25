from PIL import Image
from collections import deque
import numpy as np
import os.path
import pandas as pd

def cross_hatching_bars(img_1, img_2):
    '''
    Given two bar graphs, compare them pixel by pixel and output
    a new image that has different regions cross-hatched.
    '''
    #VARS FOR CROSS-HATCHING COUNTERS
    cols = img_1.size[0]
    col_counter = 1
    diff_counter = 1
    #CROSS-HATCH COLOUR
    cross_hatch_pixel = (0,0,0,80)
    #DEQUE FOR CROSS-HATCHING; USED TO RESET THE HATCHES BETWEEN COLUMNS
    d = deque([False,False])
    #NEW ARRAY OF (R,G,B,A) TO BE MADE INTO AN IMAGE
    new_image_data = []

    #MAIN LOOP
    for pixel_a, pixel_b in zip(img_1, img_2):
        
        if col_counter < cols: #SAME ROW IN THE IMAGE ARRAY
            
            if pixel_a != pixel_b:
                
                if sum(d) == 2:
                    diff_counter = 1
                
                if diff_counter == 1:

                    new_image_data.append(cross_hatch_pixel)
                    
                elif diff_counter == 2:

                    new_image_data.append(pixel_b)
                    diff_counter = 0           
        
                diff_counter += 1
                
                d.popleft()
                d.append(False)
            
            else:
                d.popleft()
                d.append(True)
                new_image_data.append(pixel_b)
            
            col_counter += 1

        else:
            #RESET COL COUNTER FOR EACH NEW ROW
            col_counter = 1
            #PROCESS THE LAST PIXEL IN THE ROW
            if pixel_a != pixel_b:
                
                if diff_counter == 1:
                    
                    new_image_data.append(cross_hatch_pixel)
                    
                elif diff_counter == 2:
                    
                    new_image_data.append(pixel_b)
                    diff_counter = 0           
            else:
                new_image_data.append(pixel_b)

    new_image = Image.new(img_2.mode, img_2.size)
    new_image.putdata(new_image_data)

    return new_image

def transform_frequencies(df1, df2, var_name):
    """
    Adds zero frequency to a variable that is present in one DF, but missing from another
    """

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
    #Read the first dataset
    if os.path.splitext(data_path_1)[1] == '.csv':

        df1 = pd.read_csv(data_path_1)

    elif os.path.splitext(data_path_1)[1] in ['.xlsx', '.xls']:

        df1 = pd.read_excel(data_path_1)

    #Read the second dataset
    if os.path.splitext(data_path_2)[1] == '.csv':

        df2 = pd.read_csv(data_path_2)

    elif os.path.splitext(data_path_2)[1] in ['.xlsx', '.xls']:

        df2 = pd.read_excel(data_path_2)

    return df1, df2

def dtype_mapping(input_key, reverse=False):
    """
    Performs conversion between Pandas inferred data types and user-generated ones
    Returns mapped value given an input key; parse_dates is a magic value
    """
    
    dtype_map = {'object':'Categorical', 'int':'Continuous', 'float':'Continuous', 'datetime':'Timeseries'}
    dtype_map_reverse = {'Categorical':'object', 'Continuous':'float64', 'Timeseries':'parse_dates'}
    
    if reverse:
        return dtype_map_reverse[input_key]
            
    for mapping_key in dtype_map.keys():
        if mapping_key in str(input_key):
            return dtype_map[mapping_key]
        
    return 'unknown'



