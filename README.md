[![Build Status](https://travis-ci.com/gherka/summarize_two.svg?branch=master)](https://travis-ci.com/gherka/summarize_two)

## Summarize2: visualisation tool for comparing datasets

#### Main features:
Summarize2 generates an interactive HTML report highlighting key differences between two datasets. It has:
- Command-line interface
- User-defined data type handling for when defaults fail (age interpreted as a continuous variable)
- Intelligent guessing of time and date formats. It will also try to guess if your dataset has any breaks in the time series.
- Graphical representation of the top 5 most different distributions of all combinations in any user-defined data slice shared between two datasets.

#### How to install:

Clone or download the repository, open the folder in your terminal and run `pip install .`. If you don't have all the dependencies already, run `pip install -r requirements.txt .` instead. To run an editable version of the tool add `-e` flag to `pip`.

Included in the repo are two sample datasets for comparison. One is a test modelling dataset generated using the `synthpop` R package and its original, and another is a basic example of manually tweaked data to "engineer" some of the key differences, such as the number of NAs or duplicates. 

Summarize2 has the following Python dependencies:

* Pandas (with xlrd for Excel files)
* Bokeh
* Jinja2
* Scipy
