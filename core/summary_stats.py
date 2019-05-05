import pandas as pd
import datetime

def generate_default_dict(col_dtype):
    '''
    Generate a default summary stats dictionary for each data type.
    '''

    if col_dtype == "Categorical":
        return {"DFs":{"DF1":{"Uniques":0, "NAs":0}, "DF2":{"Uniques":0, "NAs":0}}}
    
    elif col_dtype == "Continuous":
        return {"DFs":{"DF1":{"Min":0, "Max":0, "NAs":0}, "DF2":{"Min":0, "Max":0, "NAs":0}}}
    
    return {"DFs":{"DF1":{"Uniques":0, "NAs":0}, "DF2":{"Uniques":0, "NAs":0}}}

def generate_common_columns(df1, df2):
    '''
    Required early in the code to generate popup with user-selected data types
    which is why it's separated from the main generate_summary function

    Return a list
    '''

    common_col_names = [a for a in df1.columns.values if a in df2.columns.values]

    return common_col_names

def guess_date_format(date):
    '''
    A very basic date parser; only takes two common formats:
    ISO year/month/day and UK day/month/year with various separators.
    '''

    #check if date already a time object and return ISO format:
    if isinstance(date, datetime.date):
        return "%Y/%m/%d"

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

def guess_dateseries_format(series):
    '''
    Look at the first 5 values to see if they all match a date pattern.
    '''
    matches = series.head().apply(guess_date_format).unique()

    if len(matches) == 1:

        return matches[0]

    return False

def guess_date_frequency(timeseries):
    '''
    Try to guess if the sorted timestamps have any pattern to them.
    
    Pandas diff() on the sorted duplicate-less datafraeme computes
    the difference between each element with its previous row which
    gives as the time lapsed between discrete time stamps. 

    We then look at how many such differences exist and what their values
    are in days.

    If the period between two unique timestamps is between 28 and 31 days
    then we guess it's a monthly timerseries and so on.
    '''
    
    time_diff_counts = timeseries.drop_duplicates().sort_values().diff().value_counts()
    
    if len(time_diff_counts.index) == 1:
        
        if time_diff_counts.index[0].days in range(28,32):
            return "month"
        elif time_diff_counts.index[0].days in range(90,93):
            return "quarter"
        elif time_diff_counts.index[0].days in range(365, 367):
            return "year"
    
    elif time_diff_counts.index[0].days - time_diff_counts.index[1].days in range(0,3):
        
        if time_diff_counts.index[0].days in range(28,32):
            return "month"
        elif time_diff_counts.index[0].days in range(90,93):
            return "quarter"
        elif time_diff_counts.index[0].days in range(365, 367):
            return "year"
        
    else:
        return "no idea"

def guess_date_continuity(timeseries):
    '''
    Try to guess if there are any breaks in the timeseries
    '''
    
    time_diffs = timeseries.drop_duplicates().sort_values().diff()
    
    if len(time_diffs.value_counts().index) == 1:
        return "continuous"
    
    elif time_diffs.max().days - time_diffs.min().days in range(0,3):
        return "continuous"
    
    return "interruped"     

def generate_summary(df1, df2, user_dtypes):
    '''
    Main function to generate information used to populate tables in the HTML template
    Outputs pseudo-JSON code for easy parsing by Jinja2.
    '''

    #Build an (empty) nested dictionary of common column metadata
    common_cols = {
        "Categorical":{},
        "Continuous":{},
        "Timeseries":{}
    }

    common_col_names = generate_common_columns(df1, df2)

    #Find out different column names between the two datasets:
    diff_cols = ([(a, "DF1") for a in df1.columns.values if a not in df2.columns.values] + 
                 [(b, "DF2") for b in df2.columns.values if b not in df1.columns.values])

    #Find out shapes of the two datasets:
    shape_1 = df1.shape
    shape_2 = df2.shape
    
    for col in common_col_names:

        #dictionary has to be defined inside the loop to generate a new object every time
        common_cols[user_dtypes[col]][col] = generate_default_dict(user_dtypes[col])

        if user_dtypes[col] == "Categorical":

        
            #collect information from the first dataframe
            common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["Uniques"] = df1[col].nunique()
            common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["Duplicates"] = df1[col].duplicated().any()
            common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["NAs"] = sum(df1[col].isna())
        
            #collect information from the second dataframe
            common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["Uniques"] = df2[col].nunique()
            common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["Duplicates"] = df2[col].duplicated().any()
            common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["NAs"] = sum(df2[col].isna())

        
        elif user_dtypes[col] == "Continuous":

            #collect information from the first dataframe
            common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["Min"] = round(df1[col].min(),2)
            common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["Max"] = round(df1[col].max(),2)
            common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["Mean"] = round(df1[col].mean(),2)
            common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["25%"] = round(df1[col].quantile(q=0.25),2)
            common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["75%"] = round(df1[col].quantile(q=0.75),2)
            common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["NAs"] = sum(df1[col].isna())
        
            #collect information from the second dataframe
            common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["Min"] = round(df2[col].min(),2)
            common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["Max"] = round(df2[col].max(),2)
            common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["Mean"] = round(df2[col].mean(),2)
            common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["25%"] = round(df2[col].quantile(q=0.25),2)
            common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["75%"] = round(df2[col].quantile(q=0.75),2)
            common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["NAs"] = sum(df2[col].isna())

        else:

            #If a format could be inferred from the user-selected timeseries column in both datasets, 
            #process the column as timeseries, otherwise fall back to categorical columns
            if guess_dateseries_format(df1[col]) and guess_dateseries_format(df2[col]):

                #save format strings:
                format_1 = guess_dateseries_format(df1[col])
                format_2 = guess_dateseries_format(df2[col])
                format_iso = "%Y-%m-%d"

                #convert the columns' original dtype to datetype
                df1[col] = pd.to_datetime(df1[col], format=format_1)
                df2[col] = pd.to_datetime(df2[col], format=format_2)

                #collect information from the first dataframe
                common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["Format"] = format_1
                common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["Date From"] = f"{df1[col].min():{format_iso}}"
                common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["Date To"] = f"{df1[col].max():{format_iso}}"
                common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["Frequency"] = guess_date_frequency(df1[col])
                common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["Breaks?"] = guess_date_continuity(df1[col])
                common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["NAs"] = sum(df1[col].isna())

                #collect information from the second dataframe
                common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["Format"] = format_2
                common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["Date From"] = f"{df2[col].min():{format_iso}}"
                common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["Date To"] = f"{df2[col].max():{format_iso}}"
                common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["Frequency"] = guess_date_frequency(df2[col])
                common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["Breaks?"] = guess_date_continuity(df2[col])
                common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["NAs"] = sum(df2[col].isna())
            

            else:

                common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["Uniques"] = df1[col].nunique()
                common_cols[user_dtypes[col]][col]["DFs"]["DF1"]["NAs"] = sum(df1[col].isna())
                common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["Uniques"] = df2[col].nunique()
                common_cols[user_dtypes[col]][col]["DFs"]["DF2"]["NAs"] = sum(df2[col].isna())


    if len(diff_cols) == 0 :
        diff_cols = ["None"]

    table_columns = {"Categorical":["Uniques", "Duplicates", "NAs"],
                     "Continuous":["Min", "Max", "Mean", "25%", "75%", "NAs"],
                     "Timeseries":["Format", "Date From", "Date To", "Frequency", "Breaks?", "NAs"]
                     }

    output = {
        "Metadata" : {
            "different_columns": diff_cols,
            "common_columns" : common_cols,
            "table_columns": table_columns
            },
        "DFs" : {
            "DF1" : {"file_name": df1._metadata["file_name"], "shape" : shape_1},
            "DF2" : {"file_name": df2._metadata["file_name"], "shape" : shape_2}
            }
        }

    return output