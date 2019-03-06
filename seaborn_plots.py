import pandas as pd
import seaborn as sns
from PIL import Image
import matplotlib.pyplot as plt
import io
import os.path

from helper_funcs import cross_hatching_bars, transform_frequencies, read_data

def generate_plots(data_path_1, data_path_2, var_name):

    df1, df2 = read_data(data_path_1, data_path_2)

    freq_1, freq_2 = transform_frequencies(df1, df2, var_name)
    
    #Customise Seaborn using Matplotlib's parameters
    #Seaborn's set() is sneaky in bringing in a bunch of default parameters!
    sns.set(style=None, palette='deep', font='sans-serif', font_scale=1, color_codes=True, rc={
        'font.size':10,
        'figure.figsize':(3,5),
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