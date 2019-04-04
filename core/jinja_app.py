from jinja2 import Template, Environment, FileSystemLoader
import os

from core.seaborn_plots import generate_plots, generate_kde, generate_diff_plot
from core.summary_stats import generate_summary

def generate_report(df1, df2, user_dtypes, var_to_plot):

    #Generate basic dataset information
    summary = generate_summary(df1, df2, user_dtypes)

    #Generate KDE plots to be used in Jinja template

    for (i, var) in enumerate(summary['Metadata']['common_vars']['Continuous'].keys()):

        if i % 2 == 0: #even

            generate_kde(df1, df2, var, 'even')

        else:

            generate_kde(df1, df2, var, 'odd')

    #Generate custom plot to be used in Jinja template
    generate_plots(df1, df2, var_to_plot)

    #Generate Bokeh categorical frequency difference plots

    cat_diff_plots = {}
    for (j, var2) in enumerate(summary['Metadata']['common_vars']['Categorical'].keys()):

        if j % 2 == 0:

            cat_diff_plots[var2] = generate_diff_plot(df1, df2, var2, 'even')

        else:

            cat_diff_plots[var2] = generate_diff_plot(df1, df2, var2, 'odd')

    #Template Loading Machinery
    env = Environment(loader=FileSystemLoader(os.getcwd()))
        
    template = env.get_template(r'static/templates/template.jinja')

    template.stream(summary=summary, cat_plots=cat_diff_plots).dump('hello.html')