import pandas as pd
import datetime

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

def date_format_guess(date):
    """
    A very basic date parser; only takes two common formats:
    ISO year/month/day and UK day/month/year with various separators.
    """

    date_patterns = ["%Y/%m/%d", "%d/%m/%Y",
                     "%Y-%m-%d", "%d-%m-%Y",
                     "%Y.%m.%d", "%d.%m.%Y"]

    for pattern in date_patterns:      
        try:
            assert (datetime.datetime.strptime(date, pattern))
            return pattern
        except:
            pass
    return "No match"

def dateseries_format_guess(series):
    """
    Look at the first 5 values to see if they all match a date pattern.
    """
    matches = series.head().apply(date_format_guess).unique()

    if len(matches) == 1:

        return matches[0]

    return False

def date_frequency_guess(timeseries):
    
    time_diff_counts = timeseries.drop_duplicates().sort_values().diff().value_counts()
    
    if len(time_diff_counts.index) == 1:
        
        if time_diff_counts.index[0].days in range(28,32):
            return "month"
        elif time_diff_counts.index[0].days in range(90,92):
            return "quarter"
        elif time_diff_counts.index[0].days in range(365, 367):
            return "year"
    
    elif time_diff_counts.index[0].days - time_diff_counts.index[1].days in range(0,3):
        
        if time_diff_counts.index[0].days in range(28,32):
            return "month"
        elif time_diff_counts.index[0].days in range(90,92):
            return "quarter"
        elif time_diff_counts.index[0].days in range(365, 367):
            return "year"
        
    else:
        return "no idea"

def date_continuity_guess(timeseries):
    
    time_diffs = timeseries.drop_duplicates().sort_values().diff()
    
    if len(time_diffs.value_counts().index) == 1:
        return "continuous"
    
    elif time_diffs.max().days - time_diffs.min().days in range(0,3):
        return "continuous"
    
    else:
        return "interruped"     

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

            #If a format could be inferred from the user-selected timeseries column in both datasets, 
            #process the column as timeseries, otherwise fall back to categorical columns
            if dateseries_format_guess(df1[col]) and dateseries_format_guess(df2[col]):

                #save format strings:
                format_1 = dateseries_format_guess(df1[col])
                format_2 = dateseries_format_guess(df2[col])

                #convert the columns' original dtype to datetype

                df1[col] = pd.to_datetime(df1[col], format=format_1)
                df2[col] = pd.to_datetime(df2[col], format=format_2)

                #collect information from the first dataframe

                common_vars[user_dtypes[col]][col]['DFs']['DF1']['Format'] = format_1
                common_vars[user_dtypes[col]][col]['DFs']['DF1']['Date From'] = f"{df1[col].min():{format_1}}"
                common_vars[user_dtypes[col]][col]['DFs']['DF1']['Date To'] = f"{df1[col].max():{format_1}}"
                common_vars[user_dtypes[col]][col]['DFs']['DF1']['Frequency'] = date_frequency_guess(df1[col])
                common_vars[user_dtypes[col]][col]['DFs']['DF1']['Breaks?'] = date_continuity_guess(df1[col])
                common_vars[user_dtypes[col]][col]['DFs']['DF1']['NAs'] = sum(df1[col].isna())

                #collect information from the second dataframe

                common_vars[user_dtypes[col]][col]['DFs']['DF2']['Format'] = format_2
                common_vars[user_dtypes[col]][col]['DFs']['DF2']['Date From'] = f"{df2[col].min():{format_2}}"
                common_vars[user_dtypes[col]][col]['DFs']['DF2']['Date To'] = f"{df2[col].max():{format_2}}"
                common_vars[user_dtypes[col]][col]['DFs']['DF2']['Frequency'] = date_frequency_guess(df2[col])
                common_vars[user_dtypes[col]][col]['DFs']['DF2']['Breaks?'] = date_continuity_guess(df2[col])
                common_vars[user_dtypes[col]][col]['DFs']['DF2']['NAs'] = sum(df2[col].isna())
            

            else:

                common_vars[user_dtypes[col]][col]['DFs']['DF1']['Uniques'] = df1[col].nunique()
                common_vars[user_dtypes[col]][col]['DFs']['DF1']['NAs'] = sum(df1[col].isna())
                common_vars[user_dtypes[col]][col]['DFs']['DF2']['Uniques'] = df2[col].nunique()
                common_vars[user_dtypes[col]][col]['DFs']['DF2']['NAs'] = sum(df2[col].isna())


    if len(diff_vars) == 0 :
        diff_vars = ['None']

    table_columns = {'Categorical':['Uniques', 'NAs'],
                     'Continuous':['Min', 'Max', 'NAs'],
                     'Timeseries':['Format', 'Date From', 'Date To', 'Frequency', 'Breaks?', 'NAs']
                     }

    output = {
        'Metadata' : {
            'diff_vars': diff_vars,
            'common_vars' : common_vars,
            'table_columns': table_columns
            },
        'DFs' : {
            'DF1' : {'file_name': df1._metadata['file_name'], 'shape' : shape_1},
            'DF2' : {'file_name': df2._metadata['file_name'], 'shape' : shape_2}
            }
        }

    return output