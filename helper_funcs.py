from PIL import Image
from collections import deque

#CROSS-HATCHING FOR SEABORN PLOTS
def cross_hatching_bars(img_1, img_2):
    '''
    Given two bar graphs, compare them pixel by pixel and output
    a new image that has different regions cross-hatched.
    '''
    #VARS FOR CROSS-HATCHING COUNTERS
    cols = img_1.size[0]
    col_counter = 1
    diff_counter = 1
    #CROSS-HATCH COLOUR
    cross_hatch_pixel = (0,0,0,80)
    #DEQUE FOR CROSS-HATCHING; USED TO RESET THE HATCHES BETWEEN COLUMNS
    d = deque([False,False])
    #NEW ARRAY OF (R,G,B,A) TO BE MADE INTO AN IMAGE
    new_image_data = []

    #MAIN LOOP
    for pixel_a, pixel_b in zip(img_1, img_2):
        
        if col_counter < cols: #SAME ROW IN THE IMAGE ARRAY
            
            if pixel_a != pixel_b:
                
                if sum(d) == 2:
                    diff_counter = 1
                
                if diff_counter == 1:

                    new_image_data.append(cross_hatch_pixel)
                    
                elif diff_counter == 2:

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
                    
                    new_image_data.append(cross_hatch_pixel)
                    
                elif diff_counter == 2:
                    
                    new_image_data.append(pixel_b)
                    diff_counter = 0           
            else:
                new_image_data.append(pixel_b)

    new_image = Image.new(img_2.mode, img_2.size)
    new_image.putdata(new_image_data)

    return new_image