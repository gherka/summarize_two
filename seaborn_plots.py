import pandas as pd
import seaborn as sns
from PIL import Image
import matplotlib.pyplot as plt
import io

def generate_plots(data_path_1, data_path_2):

    df1 = pd.read_csv(data_path_1)
    df2 = pd.read_csv(data_path_2)
    
    #Customise Seaborn using Matplotlib's parameters
    sns.set(style='white')
    sns.set(rc={
        'axes.facecolor':'gainsboro',
        'savefig.facecolor':'gainsboro',
        'savefig.edgecolor':'gainsboro',
        'grid.linewidth':0,
        'axes.spines.left':False,
        'axes.spines.right':False,
        'axes.spines.top':False,
        'axes.spines.bottom':False,})

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

    fig_buffer_1 = io.BytesIO()
    fig_1.savefig(fig_buffer_1, format='png', bbox_inches="tight")

    fig_buffer_2 = io.BytesIO()
    fig_2.savefig(fig_buffer_2, format='png', bbox_inches="tight")

    img_1 = Image.open(fig_buffer_1).getdata()
    img_2 = Image.open(fig_buffer_2).getdata()

    #Perform pixel-by-pixel comparison of two images
    mismatches = 0
    counter = 0
    new_image = []

    for pixel_a, pixel_b in zip(img_1, img_2):
        if pixel_a == (32,32,223,255) or pixel_b == (32,32,223,255):
            counter += 1
            if pixel_a != pixel_b:
                mismatches += 1
                new_image.append((227,108,10,100))
            else:
                new_image.append(pixel_b)
        else:
            new_image.append(pixel_b)

    #Save the image with highlighted differences
    im2 = Image.new(Image.open(fig_buffer_2).mode, Image.open(fig_buffer_2).size)
    im2.putdata(new_image)

    im2.save(r'static/images/image_2.png')