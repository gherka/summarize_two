from jinja2 import Template, Environment, FileSystemLoader
import os

from core.bokeh_plots import generate_diff_plot, generate_kde_plot, generate_ridge_plot
from core.summary_stats import generate_summary

def generate_report(df1, df2, user_dtypes, ridge_spec=None):
    '''
    Main function producing final report.
    '''

    #Generate basic summary statistics information about the datasets
    summary = generate_summary(df1, df2, user_dtypes)

    #Generate KDE plots for continuous variables to be used in Jinja template
    kde_plots = {}
    for i, var in enumerate(summary["Metadata"]["common_columns"]["Continuous"].keys()):

        kde_plots[var] = generate_kde_plot(df1, df2, var, i % 2)

    #Generate Bokeh categorical frequency difference plots
    cat_diff_plots = {}
    for j, var in enumerate(summary["Metadata"]["common_columns"]["Categorical"].keys()):

        cat_diff_plots[var] = generate_diff_plot(df1, df2, var, j % 2)

    #Generate Bokeh Ridge plot:
    if ridge_spec != None:
        ridge_plot = generate_ridge_plot(df1, df2, ridge_spec)
    else:
        ridge_plot = None

    #Template loading machinery
    env = Environment(loader=FileSystemLoader(os.getcwd()))
        
    template = env.get_template(r"static/templates/template.jinja")

    template.stream(summary=summary, cat_plots=cat_diff_plots, kde_plots=kde_plots, ridge_plot=ridge_plot).dump("report.html")