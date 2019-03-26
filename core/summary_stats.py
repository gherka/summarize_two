import pandas as pd
import os.path

def generate_var_dict(var_type):
    """
    Probably not the best way to use static checks, but sufficient for now
    """

    if var_type == 'Categorical':
        return {'DFs':{'DF1':{'Uniques':0, 'NAs':0}, 'DF2':{'Uniques':0, 'NAs':0}}}
    
    elif var_type == 'Continuous':
        return {'DFs':{'DF1':{'Min':0, 'Max':0, 'NAs':0}, 'DF2':{'Min':0, 'Max':0, 'NAs':0}}}
    
    #Only Timeseries left
    return {'DFs':{'DF1':{'Uniques':0, 'NAs':0}, 'DF2':{'Uniques':0, 'NAs':0}}}
        

def generate_common_vars(df1, df2):
    """
    Required early in the code to generate popup with user-selected data types
    which is why it's separated from the main generate_summary function
    """
    common_var_names = [a for a in df1.columns.values if a in df2.columns.values]

    return common_var_names


def generate_summary(df1, df2, user_dtypes):
    """
    Main function to generate information used to populate tables in the HTML template
    Outputs pseudo-json code for easy parsing by Jinja2.
    """

    #Build an (empty) nested dictionary of common column metadata
    common_vars = {
        'Categorical':{},
        'Continuous':{},
        'Timeseries':{}
    }

    common_var_names = generate_common_vars(df1, df2)

    #Find out different variable names between the two datasets:
    diff_vars = ([(a, 'DF1') for a in df1.columns.values if a not in df2.columns.values] + 
                 [(b, 'DF2') for b in df2.columns.values if b not in df1.columns.values])

    #Find out shapes of the two datasets:
    shape_1 = df1.shape
    shape_2 = df2.shape
    
    for col in common_var_names:

        #dictionary has to be defined inside the loop to generate a new object every time
        common_vars[user_dtypes[col]][col] = generate_var_dict(user_dtypes[col])

        if user_dtypes[col] == 'Categorical':

        
            #collect information from the first dataframe
            common_vars[user_dtypes[col]][col]['DFs']['DF1']['Uniques'] = df1[col].nunique()
            common_vars[user_dtypes[col]][col]['DFs']['DF1']['NAs'] = sum(df1[col].isna())
        
            #collect information from the second dataframe
            common_vars[user_dtypes[col]][col]['DFs']['DF2']['Uniques'] = df2[col].nunique()
            common_vars[user_dtypes[col]][col]['DFs']['DF2']['NAs'] = sum(df2[col].isna())

        
        elif user_dtypes[col] == 'Continuous':

            #collect information from the first dataframe
            common_vars[user_dtypes[col]][col]['DFs']['DF1']['Min'] = df1[col].min()
            common_vars[user_dtypes[col]][col]['DFs']['DF1']['Max'] = df1[col].max()
            common_vars[user_dtypes[col]][col]['DFs']['DF1']['NAs'] = sum(df1[col].isna())
        
            #collect information from the second dataframe
            common_vars[user_dtypes[col]][col]['DFs']['DF2']['Min'] = df2[col].min()
            common_vars[user_dtypes[col]][col]['DFs']['DF2']['Max'] = df2[col].max()
            common_vars[user_dtypes[col]][col]['DFs']['DF2']['NAs'] = sum(df2[col].isna())

        else:

            #collect information from the first dataframe
            common_vars[user_dtypes[col]][col]['DFs']['DF1']['Uniques'] = df1[col].nunique()
            common_vars[user_dtypes[col]][col]['DFs']['DF1']['NAs'] = sum(df1[col].isna())
        
            #collect information from the second dataframe
            common_vars[user_dtypes[col]][col]['DFs']['DF2']['Uniques'] = df2[col].nunique()
            common_vars[user_dtypes[col]][col]['DFs']['DF2']['NAs'] = sum(df2[col].isna())


    if len(diff_vars) == 0 :
        diff_vars = ['None']

    table_columns = {'Categorical':['Uniques', 'NAs'], 'Continuous':['Min', 'Max', 'NAs'], 'Timeseries':['Uniques', 'NAs']}

    output = {
        'Metadata' : {
            'diff_vars': diff_vars,
            'common_vars' : common_vars,
            'table_columns': table_columns
            },
        'DFs' : {
            'DF1' : {'shape' : shape_1},
            'DF2' : {'shape' : shape_2}
            }
        }

    return output