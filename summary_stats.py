import pandas as pd
from collections import defaultdict
import os.path

def generate_summary(data_path_1, data_path_2):

    if (os.path.splitext(data_path_1)[1] == '.csv') & (os.path.splitext(data_path_2)[1] == '.csv'):

        df1 = pd.read_csv(data_path_1)
        df2 = pd.read_csv(data_path_2)

    if (os.path.splitext(data_path_1)[1] in ['.xlsx', '.xls']) & (os.path.splitext(data_path_1)[1] in ['.xlsx', '.xls']):

        df1 = pd.read_excel(data_path_1)
        df2 = pd.read_excel(data_path_2)

    #Find out shapes of the two datasets:
    shape_1 = df1.shape
    shape_2 = df2.shape

    #Find out different variable names between the two datasets:

    diff_vars = ([(a, 'DF1') for a in df1.columns.values if a not in df2.columns.values] + 
                 [(b, 'DF2') for b in df2.columns.values if b not in df1.columns.values])

    #Find out common variable names between the two datasets
    common_var_names = [a for a in df1.columns.values if a in df2.columns.values]

    #Build a nested dictionary of common column metadata
    common_vars = {}

    for col in common_var_names:

        #dictionary has to be defined inside the loop to generate a new object every time
        common_vars[col] = {'DFs':{'DF1':{'Uniques':0, 'NAs':0}, 'DF2':{'Uniques':0, 'NAs':0}}}

        #collect information from the first dataframe
        common_vars[col]['DFs']['DF1']['Uniques'] = df1[col].nunique()
        common_vars[col]['DFs']['DF1']['NAs'] = sum(df1[col].isna())
        
        #collect information from the second dataframe
        common_vars[col]['DFs']['DF2']['Uniques'] = df2[col].nunique()
        common_vars[col]['DFs']['DF2']['NAs'] = sum(df2[col].isna())


    if len(diff_vars) == 0 :
        diff_vars = ['None']

    output = {
        'Metadata' : {
            'diff_vars': diff_vars,
            'common_vars' : common_vars
            },
        'DFs' : {
            'DF1' : {'shape' : shape_1},
            'DF2' : {'shape' : shape_2}
            }
        }

    return output