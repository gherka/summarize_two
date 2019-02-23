from jinja2 import Template, Environment, FileSystemLoader
import os
from seaborn_plots import generate_plots
from summary_stats import generate_summary


def generate_report(data_path_1, data_path_2):

    #Generate basic dataset information
    summary = generate_summary()

    #Generate images to be used in Jinja template
    generate_plots(data_path_1, data_path_2)

    #Template Loading Machinery
    env = Environment(loader=FileSystemLoader(os.getcwd()))
        
    template = env.get_template(r'static/templates/template.html')

    template.stream(summary=summary).dump('hello.html')