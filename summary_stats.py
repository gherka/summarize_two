import pandas as pd

def generate_summary():

    df1 = pd.read_csv('data_1.csv')
    df2 = pd.read_csv('data_2.csv')

    #Find out shapes of the two datasets:
    shape_1 = df1.shape
    shape_2 = df2.shape

    #Find out common variables between the two datasets:

    diff_vars = ([(a, 'DF1') for a in df1.columns.values if a not in df2.columns.values] + 
                 [(b, 'DF2') for b in df2.columns.values if b not in df1.columns.values])


    common_vars = [a for a in df1.columns.values if a in df2.columns.values]

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