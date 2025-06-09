from tie_patterns import *
import numpy as np
from colorsys import hsv_to_rgb
from time import sleep
# Generate a pixel indices map for a DTF LED array, with a column offset

def create_matrix_map(n, offset=0):
    # Create an n x n array from 0 - (n^2)-1
    if offset:
        temp_matrix = np.arange((offset * n), (n**2) + (offset * n)).reshape(n, n)
    else:
        temp_matrix = np.arange(0, (n**2)).reshape(n, n)

    # Iterate through each row. If it's odd, reverse it
    for index, col in enumerate(temp_matrix):
        if offset:
            if (index + offset) % 2 != 0:
                temp_matrix[index] = col[::-1]
        else:
            if index % 2 != 0:
                temp_matrix[index] = col[::-1]

    # Transpose the matrix, then convert to 1-D array
    matrix_map = temp_matrix.T

    matrix_map = matrix_map.flatten()

    return matrix_map


#----------------------------------------------------------------------------
#       Create a SVG rendition of the pixel array
#----------------------------------------------------------------------------
def svg_pixels(pixel_list, brighten=1):
    # Create canvas
    svg_inline = '<svg width="128" height="128" version="1.1" xmlns="http://www.w3.org/2000/svg">\n'
    # fill canvas with black background
    #svg_inline = svg_inline +   '<rect x="0" y="0" width="128" height="128" stroke="black" fill="black" stroke-width="0"/>\n'
    # iterate through the list
    for i in range(64):
        # get the coordinates
        x = 4 * 4 * (i % 8)
        y = 4 * 4 * (i//8)
        pixel=pixel_list[i]
        red=pixel[0]
        green=pixel[1]
        blue=pixel[2]
        if brighten > 0:
            red = min(int(red * brighten),255)
            green = min(int(green * brighten),255)
            blue = min(int(blue * brighten),255)
        # build the "pixel" rectangle and append it
        pixel_str=f'<rect x="{x}" y="{y}" fill="rgb({red},{green},{blue})" width="16" height="16" stroke="white" stroke-width="1"/>\n'
        svg_inline = svg_inline + pixel_str

    #close the svg
    svg_inline = svg_inline + "</svg>"
        
    return svg_inline

#------------------------------------------------------------------
#	Write the SVG out as a file
#------------------------------------------------------------------    
def write_svg_file(pixels, label='0000', brighten=1, init=False):
    # This uses multiple files to create the webpage qubit display:
    # qubits.html is only written if init is True
    #      It contains the refresh command and the html structure, and pulls in the other two
    # pixels.svg holds the display pattern
    # pixels.lbl holds the caption
    if init:
        print("initializing html wrapper for svg display")
        try: #create the svg directory if it doesn't exist yet
            os.mkdir(r'./svg')
        except OSError as error:
            print(error)
        html_file = open (r'./svg/qubits.html',"w")
        browser_str='''<!DOCTYPE html>\r<html>\r<head>\r
                                <title>SenseHat Display</title>\r
                                <meta http-equiv="refresh" content="2.5">\r
                                </head>\r<body>\r
                                <h3>Latest Display on RPi SenseHat</h3>\r
                                <object data="pixels.html"  width='400' height='500'/ >\r
                                </body></html>'''
        #browser_str = browser_str + '<br> Qubit Pattern: ' + label + '</body></html>'
        html_file.write(browser_str)
        html_file.close()        
       
    svg_file = open (r'./svg/pixels.html',"w")
    #lbl_file = open (r'./svg/pixels.lbl',"w")
    #browser_str='''<!DOCTYPE html>\r<html>\r<head>\r
    #                            <title>SenseHat Display</title>\r
    #                            <meta http-equiv="refresh" content="1">\r
    #                            </head>\r<body>\r
    #                            <h3>Latest Display on RPi SenseHat</h3>'''
    browser_str= svg_pixels(pixels, brighten) + '\r <br/>Qubit Pattern: ' + label + '<br/><br/>\r'
    svg_file.write(browser_str)
    svg_file.close()  
    #browser_str = 'Qubit Pattern: ' + label + '\r'
    #lbl_file.write(browser_str)
    #lbl_file.close()

#-- scale lets us scale a fraction of 255
def scale(v):
    return int(v * 255)

# -- resetrainbow resets an 8x8 array of 3-value pixels back to the basic wash set up in hues
def resetrainbow(NoHat, hat, DualDisplay, hat2, show=False):
   global pixels,hues
   pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]
   pixels = [(scale(r), scale(g), scale(b)) for r, g, b in pixels]
   if (show):
       if not NoHat: hat.set_pixels(pixels)
       if DualDisplay and not NoHat: hat2.set_pixels(pixels)

def display_to_LEDs(pixel_list, neopixel_array, LED_array_indices):
    for index, pixel in enumerate(pixel_list):
        # Get RGB data from pixel list
        red, green, blue = pixel[0], pixel[1], pixel[2]

        # Get the corresponding index position on the LED array
        LED_index = LED_array_indices[index]

        # Set the appropriate pixel to the RGB value
        neopixel_array[LED_index] = (red, green, blue)

    # Display image after all pixels have been set
    
    neopixel_array.show()

#----------------------------------------------------------------
# Set the display size and rotation And turn on the display with an mask logo
#----------------------------------------------------------------
def orient():
    global hat,angle, DualDisplay
    if not NoHat:
        acceleration = hat.get_accelerometer_raw()
        x = acceleration['x']
        y = acceleration['y']
        z = acceleration['z']
        x=round(x, 0)
        y=round(y, 0)
        z=round(z, 0)
        print("current acceleration: ",x,y,z)

        if y == -1:
            angle = 180
        elif y == 1 or (SenseHatEMU and not DualDisplay):
            angle = 0
        elif x == -1:
            angle = 90
        elif x == 1:
            angle = 270
        #else:
            #angle = 180
    else:
        angle = 0
    print("angle selected:",angle)
    

    if not NoHat: hat.set_rotation(angle)
    if not NoHat and DualDisplay: hat2.set_rotation(0)


def set_hat(UseEmulator, UseNeo, NeoTiled, matrix_map, RQ2_array_indices):
    SenseHatEMU = False
    hatcounter = 0
    if not UseEmulator:
        print ("... importing SenseHat and looking for hardware")
        try:
            from sense_hat import SenseHat
            hat = SenseHat() # instantiating hat right away so we can use it in functions
        except:
            print ("... problem finding SenseHat")
            UseEmulator = True
            print("       ....trying SenseHat Emulator instead")

    if UseEmulator:
        print ("....importing SenseHat Emulator")
        try: 
            from sense_emu import SenseHat         # class for controlling the SenseHat emulator. API is identical to the real SenseHat class
            hat = SenseHat() # instantiating hat emulator so we can use it in functions
            while not SenseHatEMU:
                try:	#This function will error if the emulator program hasn't started
                    hat.set_imu_config(True,True,True) #initialize the accelerometer simulation
                    print("waiting for SenseHat emulator to start: iteration ",hatcounter,"/60")
                except:
                    sleep(1)
                    hatcounter += 1
                else:
                    SenseHatEMU = True
                    if hatcounter >=10: NoHat = True
        except:
            NoHat = True

    if UseNeo:
        print("importing neopixel library...")
        try:
            import board
            import neopixel_spi as neopixel
        except Exception as e:
            print("Error importing neopixel library: ", e)
        try:
            # Neopixel constants
            if NeoTiled: 
                NUM_PIXELS = 192
                PIXEL_ORDER = neopixel.RGB
            else: 
                NUM_PIXELS = 256
                PIXEL_ORDER = neopixel.GRB
            BRIGHTNESS = 0.10

            # Neopixel initialization
            spi = board.SPI()

            neopixel_array = neopixel.NeoPixel_SPI(
                spi,
                NUM_PIXELS,
                pixel_order=PIXEL_ORDER,
                brightness=BRIGHTNESS,
                auto_write=False,
            )
            #neopixel_array.clear()
            #neopixel_array.show()
        except Exception as e:
            print("Error initilizating Neopixel board: ", e)

    else:
        if DualDisplay: # if you have a Sensehat but want the emulator running also. 
            #Note that the svg file is always written, so you can open the ./svg/qubits.html file instead 
            #	to see the qubit display instead of using the emulator for a second display
            from sense_emu import SenseHat         # class for controlling the SenseHat
            hat2 = SenseHat() # instantiating hat emulator so we can use it in functions
            while not SenseHatEMU:
                try:
                    hat2.set_imu_config(True,True,True) #initialize the accelerometer simulation
                except:
                    sleep(1)
                else:
                    SenseHatEMU = True

    if NeoTiled:    LED_array_indices = RQ2_array_indices
    else:           LED_array_indices = matrix_map

    return [hat, hat2, LED_array_indices, SenseHatEMU]