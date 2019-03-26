from jinja2 import Template, Environment, FileSystemLoader
import os

from core.seaborn_plots import generate_plots
from core.summary_stats import generate_summary

def generate_report(df1, df2, user_dtypes, var_to_plot):

    #Generate basic dataset information
    summary = generate_summary(df1, df2, user_dtypes)

    #Generate images to be used in Jinja template
    generate_plots(df1, df2, var_to_plot)

    #Template Loading Machinery
    env = Environment(loader=FileSystemLoader(os.getcwd()))
        
    template = env.get_template(r'static/templates/template.html')

    template.stream(summary=summary).dump('hello.html')