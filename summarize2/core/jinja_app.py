'''
Module handling the genration of all HTML components
'''

# Standard library imports
from io import StringIO
from pathlib import Path
from os.path import join

# External library imports
import bokeh
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
    if kwargs.get('ridge', None):
        ridge_plot = generate_ridge_plot(df1, df2, kwargs['ridge'])
    else:
        ridge_plot = None

    #Generate Bokeh Crosstab plot:
    if kwargs.get('xtab', None):
        xtab_plot = generate_xtab_plot(df1, df2, kwargs['xtab'])
    else:
        xtab_plot = None


    #Template loading machinery
    root_path = package_dir("static")

    #Check if Python version of Bokeh matches the locally saved version
    #We prefer to load from CDN with a local backup, but using an older
    #version might break some Bokeh functionality

    local_bokeh_scripts = list(Path(join(root_path, "scripts")).glob("bokeh*"))

    if len(local_bokeh_scripts) > 1:
        print("WARNING: More than 1 Bokeh script found. Loading from CDN.")
        local_bokeh_version = "None"
    elif len(local_bokeh_scripts) == 1:
        local_bokeh_version = local_bokeh_scripts[0].stem[6:11]
        if local_bokeh_version != bokeh.__version__:
            print("WARNING: local copy of the Bokeh script doesn't match the Python environment.")
    else:
        print("WARNING: No local backup script of Bokeh is available. Loading from CDN.")

    env = Environment(loader=FileSystemLoader(root_path))
        
    template = env.get_template("templates/template.jinja")

    output = StringIO()

    template.stream(
        root=root_path,
        cdn_bokeh_version=bokeh.__version__.split("."),
        local_bokeh_version=local_bokeh_version,
        summary=summary,
        cat_plots=cat_diff_plots,
        kde_plots=kde_plots,
        xtab_plot=xtab_plot,
        ridge_plot=ridge_plot).dump(output)

    return output.getvalue()
