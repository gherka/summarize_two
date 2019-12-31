'''
Reference tests for Summarize2
'''
# Standard library imports
import unittest
from unittest.mock import patch
import argparse
from pathlib import Path
from io import StringIO
import re

# Summarize2 imports
from summarize2.core.helper_funcs import package_dir

# Module under test
from summarize2.command import bootstrap  as tm

class referenceTests(unittest.TestCase):
    '''
    Test command line arguments and running logic of Summarize2
    '''

    @patch('argparse.ArgumentParser.parse_args')
    def test_basic_dataset_comparison(self, mock_args):
        '''
        Run summarize2 with two basic .csv from sample data and
        compare it with the reference report
        '''

        test_output = StringIO()
        ref_path = Path(package_dir('command', 'tests', 'ref', 'ref_basic.html'))
        with open(ref_path, 'r') as f:
            ref_output = f.read()

        mock_args.return_value = argparse.Namespace(
            first_dataset=Path(package_dir('sample data', 'basic_1.csv')),
            second_dataset=Path(package_dir('sample data', 'basic_2.csv')),
            verbose=True,
            xtab=None,
            output=test_output
        )

        test_dtypes = {
            "age": "Categorical",
            "episodes": "Continuous",
            "gender": "Categorical",
            "hbres_name": "Categorical",
            "length_of_stay": "Continuous",
            "reporting_date": "Timeseries"
        }

        tm.main(user_dtypes=test_dtypes)

        #Bokeh adds a 4 digit ID to various elements that are unique to each generation
        #also, the paths in the files can be upper or lower case
        #by casting everything into upper some information (__ndarray__) is lost!
        a_clean = re.sub(r'"\d{4}"', '', ref_output).upper()
        b_clean = re.sub(r'"\d{4}"', '', test_output.getvalue()).upper()

        a = ''.join(sorted(a_clean))
        b = ''.join(sorted(b_clean))
        
        test_output.close()

        assert a == b

    @patch('argparse.ArgumentParser.parse_args')
    def test_synthpop_dataset_comparison(self, mock_args):
        '''
        Run summarize2 with Synthpop-generated data against its
        original from sample data and compare it with the reference
        report
        '''

        test_output = StringIO()
        ref_path = Path(package_dir('command', 'tests', 'ref', 'ref_synthpop.html'))
        with open(ref_path, 'r') as f:
            ref_output = f.read()

        mock_args.return_value = argparse.Namespace(
            first_dataset=Path(package_dir('sample data', 'Original.csv')),
            second_dataset=Path(package_dir('sample data', 'Synth.csv')),
            verbose=True,
            xtab=None,
            output=test_output
        )

        test_dtypes = {

            "agegr": "Categorical",
            "depress": "Continuous",
            "edu": "Categorical",
            "income": "Continuous",
            "marital": "Categorical",
            "sex": "Categorical",
            "socprof": "Categorical",
            "trust": "Categorical",
            "trustfam": "Categorical",
            "trustneigh": "Categorical",
            "weight": "Continuous",
        }

        tm.main(user_dtypes=test_dtypes)

        #Bokeh adds a 4 digit ID to various elements that are unique to each generation
        #also, the paths in the files can be upper or lower case
        #by casting everything into upper some information (__ndarray__) is lost!
        a_clean = re.sub(r'"\d{4}"', '', ref_output).upper()
        b_clean = re.sub(r'"\d{4}"', '', test_output.getvalue()).upper()

        a = ''.join(sorted(a_clean))
        b = ''.join(sorted(b_clean))
        
        test_output.close()

        assert a == b
