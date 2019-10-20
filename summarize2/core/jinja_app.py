'''
Module handling the genration of all HTML components
'''

# Standard library imports
from io import StringIO

# External library imports
from jinja2 import Environment, FileSystemLoader

# Summarize2 imports
from ..core.bokeh_plots import (
    generate_diff_plot, generate_kde_plot,
    generate_ridge_plot, generate_xtab_plot)
from ..core.summary_stats import generate_summary
from ..core.helper_funcs import package_dir

def generate_report(df1, df2, user_dtypes, **kwargs):
    '''
    Main function producing the report.
    '''

    #Generate basic summary statistics about the datasets
    summary = generate_summary(df1, df2, user_dtypes)

    #Generate KDE plots for continuous variables to be used in Jinja template
    kde_plots = {}
    for i, var in enumerate(summary["Metadata"]["common_columns"]["Continuous"]):

        kde_plots[var] = generate_kde_plot(df1, df2, var, i % 2)

    #Generate Bokeh categorical frequency difference plots
    cat_diff_plots = {}
    for j, var in enumerate(summary["Metadata"]["common_columns"]["Categorical"]):

        cat_diff_plots[var] = generate_diff_plot(df1, df2, var, j % 2)

    #Generate Bokeh Ridge plot:
    if kwargs['ridge']:
        ridge_plot = generate_ridge_plot(df1, df2, kwargs['ridge'])
    else:
        ridge_plot = None

    #Generate Bokeh Crosstab plot:
    if kwargs['xtab']:
        xtab_plot = generate_xtab_plot(df1, df2, kwargs['xtab'])
    else:
        xtab_plot = None


    #Template loading machinery
    root_path = package_dir("static")

    env = Environment(loader=FileSystemLoader(root_path))
        
    template = env.get_template("templates/template.jinja")

    output = StringIO()

    template.stream(
        root=root_path,
        summary=summary,
        cat_plots=cat_diff_plots,
        kde_plots=kde_plots,
        xtab_plot=xtab_plot,
        ridge_plot=ridge_plot).dump(output)

    return output.getvalue()
