import pandas as pd
import seaborn as sns
from PIL import Image
import matplotlib.pyplot as plt
import io
from collections import deque

def generate_plots(data_path_1, data_path_2, var_name):

    df1 = pd.read_csv(data_path_1)
    df2 = pd.read_csv(data_path_2)
    
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

    max_y = max(max(df1[var_name].value_counts()), max(df1[var_name].value_counts()))

    #Frequency graph of the first dataset
    fig_1, ax_1 = plt.subplots()
    ax_1.set_ylim(0,max_y)
    sns.countplot(y=var_name, data=df1, color='coral')

    #Frequency graph of the seconda dataset
    #interesting point: if draw in different sorting orders, the pixel-by-pixel will fail
    #order=df2[var_name].value_counts().index
    fig_2, ax_2 = plt.subplots()
    ax_2.set_ylim(0,max_y)
    sns.countplot(y=var_name, data=df2, color='coral')

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


        #UPDATE CODE FOR CROSS-HATCHING OF DIFFERENCES ON PLOTS: REVIEW!!!!
        cols = img_1.size[0]
        col_counter = 1
        diff_counter = 1

        d = deque([False,False])

        for pixel_a, pixel_b in zip(img_1, img_2):
            
            if col_counter < cols:
                
                #DO STUFF IN ITERATION ON COLUMNS PER SINGLE ROW
                
                if pixel_a != pixel_b:
                    
                    if sum(d) == 2:
                        diff_counter = 1
                    
                    #DO STUFF THAT DEPENDS OF IT BEING FIRST TIME DIFFERENT
                    
                    if diff_counter == 1:
                        
                        cross_hatch = True
                        new_image_data.append((0,0,0,80))
                        
                    elif diff_counter == 2:
                        
                        cross_hatch = False
                        new_image_data.append(pixel_b)
                        diff_counter = 0           
            
                    diff_counter += 1
                    
                    d.popleft()
                    d.append(False)
                
                else:
                    d.popleft()
                    d.append(True)
                    new_image_data.append(pixel_b)
                
                col_counter += 1

            else:
                #RESET COL COUNTER FOR EACH NEW ROW
                col_counter = 1
                #PROCESS THE LAST PIXEL IN THE ROW
                if pixel_a != pixel_b:
                    
                    if diff_counter == 1:
                        
                        cross_hatch = True
                        new_image_data.append((0,0,0,80))
                        
                    elif diff_counter == 2:
                        
                        cross_hatch = False
                        new_image_data.append(pixel_b)
                        diff_counter = 0           
                else:
                    new_image_data.append(pixel_b)

        new_image = Image.new(Image.open(fig_buffer_B).mode, Image.open(fig_buffer_B).size)
        new_image.putdata(new_image_data)

        return new_image
    
    #Save the image with highlighted differences
    new_bar_chart = pixel_by_pixel(fig_1, fig_2)
    new_bar_chart.save(r'static/images/image_2.png')