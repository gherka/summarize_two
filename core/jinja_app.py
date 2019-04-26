from jinja2 import Template, Environment, FileSystemLoader
import os

from core.seaborn_plots import generate_kde
from core.bokeh_plots import generate_diff_plot, generate_ridge_plot
from core.summary_stats import generate_summary

def generate_report(df1, df2, user_dtypes, ridge_spec=None):

    #Generate basic dataset information
    summary = generate_summary(df1, df2, user_dtypes)

    #Generate KDE plots to be used in Jinja template
    for (i, var) in enumerate(summary['Metadata']['common_vars']['Continuous'].keys()):

        if i % 2 == 0: #even

            generate_kde(df1, df2, var, 'even')

        else:

            generate_kde(df1, df2, var, 'odd')

    #Generate Bokeh categorical frequency difference plots
    cat_diff_plots = {}
    for (j, var2) in enumerate(summary['Metadata']['common_vars']['Categorical'].keys()):

        if j % 2 == 0:

            cat_diff_plots[var2] = generate_diff_plot(df1, df2, var2, 'even')

        else:

            cat_diff_plots[var2] = generate_diff_plot(df1, df2, var2, 'odd')

    # Generate Bokeh Ridge plot:
    if ridge_spec != None:
        ridge_plot = generate_ridge_plot(df1, df2, ridge_spec['cols'], ridge_spec['num_col'], ridge_spec['indices'])
    else:
        ridge_plot = None

    #Template Loading Machinery
    env = Environment(loader=FileSystemLoader(os.getcwd()))
        
    template = env.get_template(r'static/templates/template.jinja')

    template.stream(summary=summary, cat_plots=cat_diff_plots, ridge_plot=ridge_plot).dump('hello.html')