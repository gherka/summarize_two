import pandas as pd
import numpy as np
import json

import seaborn as sns
from PIL import Image
import matplotlib.pyplot as plt

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.embed import json_item

import io
import os.path

from core.helper_funcs import cross_hatching_bars, transform_frequencies, read_data

def generate_plots(df1, df2, var_name):
    #clear current (if any) figure and axes
    plt.clf()
    plt.cla()

    freq_1, freq_2 = transform_frequencies(df1, df2, var_name)
   
    #Customise Seaborn using Matplotlib's parameters
    #Seaborn's set() is sneaky in bringing in a bunch of default parameters!
    sns.set(style=None, palette='deep', font='sans-serif', font_scale=1, color_codes=True, rc={
        'font.size':10,
        'figure.figsize':(3, len(freq_1[0])*0.5),
        'xtick.labelsize':'small',
        'ytick.labelsize': 'small',
        'xtick.major.size':5,
        'xtick.major.width':0.5,
        'ytick.major.size':0,
        'axes.facecolor':'gainsboro',
        'savefig.facecolor':'gainsboro',
        'savefig.edgecolor':'gainsboro',
        'grid.linewidth':0,
        'axes.spines.left':False,
        'axes.spines.right':False,
        'axes.spines.top':False,
        'axes.spines.bottom':False
        })

    max_x = max(max(df1[var_name].value_counts()), max(df2[var_name].value_counts()))

    #Frequency graph of the first dataset
    fig_1, ax_1 = plt.subplots()
    ax_1.set_xlim(0, max_x)
    sns.barplot(x=freq_1[1], y=freq_1[0], color='coral', ax=ax_1)

    #Frequency graph of the seconda dataset
    fig_2, ax_2 = plt.subplots()
    ax_2.set_xlim(0, max_x)
    sns.barplot(x=freq_2[1], y=freq_2[0], color='coral', ax=ax_2)

    fig_1.savefig(r'static/images/image_1.png', bbox_inches="tight")

    #Perform pixel-by-pixel comparison of two images
    def pixel_by_pixel(fig_A, fig_B):
        '''
        Given two figures (fig_A, fig_B) does pixel-by-pixel and returns
        a new image that has highlights where the two images are different
        '''

        fig_buffer_A = io.BytesIO()
        fig_A.savefig(fig_buffer_A, format='png', bbox_inches="tight")

        fig_buffer_B = io.BytesIO()
        fig_B.savefig(fig_buffer_B, format='png', bbox_inches="tight")

        img_1 = Image.open(fig_buffer_A).getdata()
        img_2 = Image.open(fig_buffer_B).getdata()

        return cross_hatching_bars(img_1, img_2)

    #Save the image with highlighted differences
    new_bar_chart = pixel_by_pixel(fig_1, fig_2)
    new_bar_chart.save(r'static/images/image_2.png')

def generate_kde(df1, df2, var_name, shade):


    #clear current (if any) figure and axes
    plt.clf()
    plt.cla()

    #banded row colors: 

    if shade == 'even':
        band_color = '#e6e5e3'
    else:
        band_color = 'gainsboro'

    #Customise Seaborn using Matplotlib's parameters
    #Seaborn's set() is sneaky in bringing in a bunch of default parameters!
    sns.set(style=None, palette='deep', font='sans-serif', font_scale=1, color_codes=True, rc={
        'font.size':10,
        'figure.figsize':(5, 5),
        'xtick.labelsize':'small',
        'ytick.labelsize': 'small',
        'xtick.major.size':5,
        'xtick.major.width':0.5,
        'ytick.major.size':0,
        'axes.facecolor': band_color,
        'savefig.facecolor':band_color,
        'savefig.edgecolor':band_color,
        'grid.linewidth':0,
        'axes.spines.left':False,
        'axes.spines.right':False,
        'axes.spines.top':False,
        'axes.spines.bottom':False
        })

    fig, ax = plt.subplots()

    sns.kdeplot(df1[var_name].dropna().values, shade=True, label="DF1", ax=ax)
    sns.kdeplot(df2[var_name].dropna().values, shade=True, label="DF2", ax=ax)

    fig.savefig(f'static//images//kde_{var_name}.png', bbox_inches="tight")

def generate_diff_plot(df1, df2, var_name, shade):
    """
    Create a json representation of a Bokeh plot to be embedded in the template
    """

    #banded row colors: 
    if shade == 'even':
        band_color = '#e6e5e3'
    else:
        band_color = 'gainsboro'

    freq_1, freq_2 = transform_frequencies(df1, df2, var_name)

    bokeh_df = pd.DataFrame({'VAR':[str(x) for x in freq_1[0]],
                        'DF1':freq_1[1],
                        'DF2':freq_2[1],
                        'DIFF': freq_2[1] - freq_1[1],
                        'COLOR': np.where(freq_2[1] - freq_1[1] > 0, '#527563', '#876388')}
                      )

    source = ColumnDataSource(bokeh_df.sort_values(by='DIFF'))

    TOOLTIPS = [
        ("Name", "@VAR"),
        ("DF1 Value", "@DF1"),
        ("DF2 Value", "@DF2"),
        ("Difference", "@DIFF")
    ]

    p = figure(x_range=source.data['VAR'],
           plot_height=170,
           plot_width=165,
           tools="pan,wheel_zoom,hover",
           active_scroll="wheel_zoom",
           toolbar_location = None,
           tooltips=TOOLTIPS)

    p.vbar(x='VAR', top='DIFF', width=0.9, alpha=0.8, line_color='white', color='COLOR', source=source)
    p.ray(x=[0], y=[0], length=len(source.data['VAR']), angle=0, line_width=0.5, color='black')

    p.xaxis.visible = False
    p.yaxis.minor_tick_line_alpha = 0
    p.grid.visible = False
    p.background_fill_color = band_color
    p.outline_line_color = band_color
    p.border_fill_color = band_color
    p.yaxis.axis_line_width = 0.5

    item_text = json.dumps(json_item(p))

    return item_text