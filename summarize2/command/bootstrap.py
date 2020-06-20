'''
Launch module of the tool.
Defines command line parameters, runs through logic.
'''

# Standard library imports
import argparse
import textwrap
import sys
import os
import io

# Summarize2 imports
from ..core.jinja_app import generate_report
from ..core.summary_stats import generate_common_columns
from ..core.helper_funcs import (
    read_data, path_checker, open_report_in_default_browser,
    launch_temp_file, convert_dtypes)

def main(**kwargs):
    '''
    Kwargs added for ease of testing.
    '''

    #Set default verbosity
    sys.tracebacklimit = 0

    desc = textwrap.dedent('''\
        ------------------------------------------------------
        Summarize2: Comparing two datasets with a visual twist  \n
        Create an HTML report with metrics to show how similar
        or different two datasets are between each other.
        ------------------------------------------------------
        ''')

    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.RawTextHelpFormatter
        )

    parser.add_argument(
        "first_dataset",
        type=path_checker
        )

    parser.add_argument(
        "second_dataset",
        type=path_checker
        )

    parser.add_argument(
        "--ridge", "-r",
        default=False,
        action="store_true",
        help="not implemented yet",
        )

    parser.add_argument(
        "--xtab", "-xtab",
        action="store_true",
        help="add a crosstab section to the report",
        )

    parser.add_argument(
        "--verbose", "-v",
        default=False,
        action="store_true",
        help="control traceback length for debugging errors",
        )
    
    parser.add_argument(
        "--output", "-o",
        help="file path where to save the report, including .html",
        )
 
    args = parser.parse_args(sys.argv[1:])

    #Default verbosity is set to 0
    if args.verbose:
        sys.tracebacklimit = 1000

    #Read in files as dataframes
    df1, df2 = read_data(args.first_dataset, args.second_dataset)
    common_columns = generate_common_columns(df1, df2)

    #Ask user to confirm data types for each column (via editable temp text file)
    dtypes = df1[common_columns].dtypes.apply(convert_dtypes).to_dict()

    #Pop user_dtypes if passed, otherwise launch text editor for user imput
    user_dtypes = kwargs.pop('user_dtypes', None)
    
    if not user_dtypes:
        user_dtypes = launch_temp_file(file_type="dtypes", dtypes=dtypes)

    #Select only non-numeric columns
    common_cat_cols = [k for k, v in user_dtypes.items() if v != "Continuous"]

    #Run through optional features of the report:
    ridge_spec = None
    xtab_spec = None

    if args.xtab:

        xtab_spec = launch_temp_file(file_type="xtab", common_cols=common_cat_cols)

    #Generate report
    report = generate_report(df1, df2, user_dtypes, xtab=xtab_spec, ridge=ridge_spec)

    #Write to file or IO
    if args.output:
        #if output is StringIO() then write, don't close, don't open browser
        if isinstance(args.output, io.TextIOBase):
            args.output.write(report)
        else:
            #handle the string as if it's a path string
            file_path = args.output
            with open(file_path, 'w+') as f:
                f.write(report)
            open_report_in_default_browser(file_path)

    else:
        file_path = os.path.join(os.getcwd(), "report.html")
        with open(file_path, 'w+') as f:
            f.write(report)
        open_report_in_default_browser(file_path)
