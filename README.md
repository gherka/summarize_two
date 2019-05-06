## Summarize2: visualisation tool for comparing datasets

#### Main features:
Summarize2 generates an interactive HTML report highlighting key differences between two datasets. It has:
- An intuitive GUI
- User-defined data type handling for when defaults fail (age interpreted as a continuous variable)
- Intelligent guessing of time and date formats. It will also try to guess if your dataset has any breaks in the time series.
- Graphical representation of the top 5 most different distributions of all combinations in any user-defined data slice shared between two datasets.

#### How to install:

Clone or download the repo and run `summarize2.py` from the command line.

Included in the repo are two sample datasets for comparison. One is a test modelling dataset generated using the `synthpop` R package and its original, and another is a basic example of manually tweaked data to "engineer" some of the key differences, such as the number of NAs or duplicates. 

Summarize2 has the following Python dependencies:

* Pandas (with xlrd for Excel files)
* Bokeh
* Jinja2
* Scipy
