import pandas as pd
import seaborn as sns
from PIL import Image
import matplotlib.pyplot as plt
import io

def generate_plots(data_path_1, data_path_2):

    df1 = pd.read_csv(data_path_1)
    df2 = pd.read_csv(data_path_2)
    
    #Customise Seaborn using Matplotlib's parameters
    #Seaborn's set() is sneaky in bringing in a bunch of default parameters!
    sns.set(style=None, palette='deep', font='sans-serif', font_scale=1, color_codes=True, rc={
        'font.size':8,
        'axes.facecolor':'gainsboro',
        'savefig.facecolor':'gainsboro',
        'savefig.edgecolor':'gainsboro',
        'grid.linewidth':0,
        'axes.spines.left':False,
        'axes.spines.right':False,
        'axes.spines.top':False,
        'axes.spines.bottom':False
        })

    max_y = max(df1.Value.max(), df2.Value.max())

    #Bar graph of the first dataset
    fig_1, ax_1 = plt.subplots()
    ax_1.set_ylim(0,max_y)
    sns.barplot(x=df1.Category, y=df1.Value, color='blue', ax=ax_1)

    #Bar graph of the seconda dataset
    fig_2, ax_2 = plt.subplots()
    ax_2.set_ylim(0,max_y)
    sns.barplot(x=df2.Category, y=df2.Value, color='blue', ax=ax_2)

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

        mismatches = 0
        counter = 0
        new_image_data = []

        for pixel_a, pixel_b in zip(img_1, img_2):
            if pixel_a == (32,32,223,255) or pixel_b == (32,32,223,255):
                counter += 1
                if pixel_a != pixel_b:
                    mismatches += 1
                    new_image_data.append((227,108,10,100))
                else:
                    new_image_data.append(pixel_b)
            else:
                new_image_data.append(pixel_b)

        new_image = Image.new(Image.open(fig_buffer_A).mode, Image.open(fig_buffer_A).size)
        new_image.putdata(new_image_data)

        return new_image
    
    #Save the image with highlighted differences
    new_bar_chart = pixel_by_pixel(fig_1, fig_2)
    new_bar_chart.save(r'static/images/image_2.png')