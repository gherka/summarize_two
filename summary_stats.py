import pandas as pd

def generate_summary():

    df1 = pd.read_csv('data_1.csv')
    df2 = pd.read_csv('data_2.csv')

    #Find out shapes of the two datasets:
    shape_1 = df1.shape
    shape_2 = df2.shape

    #Find out common variables between the two datasets:
    common_vars = [col_a for col_a, col_b in zip(df1.columns.values, df2.columns.values) if col_a == col_b]

    output = {
        'Metadata' : common_vars,
        'DFs' : {
            'DF1' : {'shape' : shape_1},
            'DF2' : {'shape' : shape_2}
            }
        }

    return output