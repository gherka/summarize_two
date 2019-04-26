import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from core.helper_funcs import transform_frequencies

def generate_kde(df1, df2, var_name, shade):
    '''
    Saves static images of KDE plots produced by Seaborn.
    Consider switching to Bokeh generated plots for
    complete online/offline switching depending on resource loading.
    Seaborn static images mean only offline (no sharing standalone HTML)
    is possible.
    '''

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