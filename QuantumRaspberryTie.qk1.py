#----------------------------------------------------------------------
#     QuantumRaspberryTie.qk1_local
#       by KPRoche (Kevin P. Roche) (c) 2017,2018,2019,2020,2021,2022.2024
#
#     NEW RELEASE 
#     April 2024 to accomodate the official release of Qiskit 1.0
#     using new QiskitRuntime libraries and call techniques;
#     runs OPENQASM code on an IBM Quantum backend or simulator 
#     Display the results using the 8x8 LED array on a SenseHat (or SenseHat emulator)
#     Will Default to local simulator because the cloud simulator is being retired.
#
#     Will Connect and authenticate to the IBM Quantum platform via the QiskitRuntime module (if necessary)
#     
#        NEW default behavior:
#               Spins up a 5-qubit test backend (local simulator) based on FakeManilaV2
#                   in a "bowtie" arrangement based on older processors
#               New Qiskit-logo inspired "thinking" graphic
#        NEW backend options:
#           -b:aer | spins up a local Aer simulator
#           -b:aer_noise or -b:aer_model | spins up a local Aer simulator with a noise model 
#               based on the least busy real processor for your account (this does require access to
#               the IBM Quantum processors and account credentials properly saved via QiskitRuntime
#           -b:least | will run code once on the least busy *real* backend for your account
#               NOTE: this may take hours before the result returns
#           -b:[backend_name] | will use the specified backend if it is available (see note above)
#        NEW display options
#           NOTE: if multiple options are specified the last one in the parameters will be applied
#           hex or -hex | displays on a 12 qubit pattern 
#                    (topologically identical to the heavy hex in IBM processors) 
#           d16 or -d16 | displays on a 16 qubit pattern
#               NOTE: overrides default or tee option for 5 qubit code!
#               NOTE: if your quantum circuit has fewer qubits than available in the display mode, 
#                   unmeasured qubits will be displayed in purple
#
#        NEW interactive options 
#           -input | prompts you to add more parameters to what was on the command line
#           -select | prompts you for the backend option before initializing
#        OTHER options:
#           -tee | switches to a tee-shaped 5-qubit arrangement
#           -16 or 16 | loads a 16-qubit QASM file and switches to a 16-bit display arrangement
#               NOTE: hex display mode will override the 16 qubit display and show only the first 12
#           -noq | does not show a logo during the rainbow "thinking" moment; instead rainbows the qubit display
#           -e | will attempt to spin up a SenseHat emulator display on your desktop. 
#           -d | will attempt to display on BOTH the SenseHat and a emulator display
#               These require that both the libraries and a working version of the emulator executable be present
#           -f:filename load an alternate QASM file
# ----------------------------- pre Qiskit 1.0 History -----------------------
#
#     April 2023 -- added dual display option. If sensehat is available, will spin up a second emulator to show
#                    on the desktop
#     Nov 2022 -- Cleaned up -local option to run a local qasm simulator if supported
#
#     Feb 2020 -- Added fix to IBM Quantum Experience URL (Thanks Jan Lahman)
#
#     October 2019 -- added extra command line parameters. Can force use of Sensehat emulator, or specify backend
#                        (specifying use of a non-simulator backend will disable loop)
#     October 2019 -- will attempt to load SenseHat and connect to hardware.
#                        If that fails, then loads and launches SenseHat emulator for display instead
#
#     September 2019 -- adaptive version can use either new (0.3) ibmq-provider with provider object
#                         or older (0.2) IBMQ object
#     July 2019 -- convert to using QISKIT full library authentication and quantum circuit
#                    techniques
#     March 2018 -- Detect a held center switch on the SenseHat joystick to trigger shutdown
#     
#     Original (2017) version
#       Spin off the display functions in a separate thread so they can exhibit
#             smooth color changes while "thinking"
#       Use a ping function to try to make sure the website is available before
#             sending requests and thus avoid more hangs that way
#       Move the QASM code into an outside file
#
#----------------------------------------------------------------------


# import the necessary modules
print("importing libraries...")
print("       ....sys")
import sys                             # used to check for passed filename
print("       ....os")
import os                              # used to find script directory
print("       ....requests")
import requests                        # used for ping
print("       ....threading")
from threading import Thread           # used to spin off the display functions
print("       ....colorsys")
from colorsys import hsv_to_rgb        # used to build the color array
print("       ....time")
from time import process_time          # used for loop timer
print("       ....sleep")
from time import sleep                 #used for delays
print("       ....qiskit QiskitRuntimeService")
from qiskit_ibm_runtime import QiskitRuntimeService               # classes for accessing IBM Quantum online services
print("       ....QuantumCircuit and transpile")
from qiskit import QuantumCircuit, transpile, qiskit
from qiskit.providers import JobStatus
print("     .....simple local emulator (fakeManila)")
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
print ("    .....Aer for building local simulators")#importing Aer to use local simulator")
from qiskit_aer import Aer
print("       ....warnings")
import warnings

IBMQVersion = qiskit.__version__
print(IBMQVersion)


#Initialize then check command arguments 
UseEmulator = False
DualDisplay = False
QWhileThinking = True
UseTee = False
UseHex = False
UseQ16 = False
UseLocal = True
backendparm = '[localsim]'
SelectBackend = False #for interactive selection of backend
fake_name = "FakeManilaV2"
qubits_needed = 5  #default size for the five-qubit simulation
AddNoise = False
debug = False
qasmfileinput='expt.qasm'

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
                                <object data="pixels.html"/ height='425' width='400'>\r
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
    


# -- prompt for any extra arguments if specified
print(sys.argv)
print ("Number of arguments: ",len(sys.argv))

# first check for interactive input request
if (len(sys.argv)>1):  
    parmlist = sys.argv
    if "-input" in sys.argv:
        bparmstr = input("add any additional parameters to the initial program call:\n")
        if len(bparmstr) > 0:
            bparms = bparmstr.split()
            print("Command parms:",parmlist,"extra parms:",bparms)
            parms = parmlist + bparms
    else: parms = parmlist
    print("all parms:",parms)
    if debug: input("Press Enter to continue")

# now process the option parameters
    #for p in range (1, len(sys.argv)):
    for p in range (1, len(parms)):
        parameter = parms[p]
        if type(parameter) is str:
            print("Parameter ",p," ",parameter)
            if 'debug' in parameter: debug = True
            if ('16' == parameter or "-16" == parameter): qasmfileinput='16'
            if '-local' in parameter: UseLocal = True      # use the aer local simulator instead of the web API
            if '-nois' in parameter:                       # add noise model to local simulator
                UseLocal = True
                AddNoise = True
            if '-noq' in parameter: QWhileThinking = False # do the rainbow wash across the qubit pattern while "thinking"
            if '-tee' in parameter: 
                UseTee = True          # use the new tee-shaped 5 qubit layout for the display
                
            if 'hex' in parameter: 
                UseHex = True          # use the heavy hex 12 qubit layout for the display
                UseTee = False         # (and give it precedence over the tee display
            if 'q16' in parameter: 
                UseQ16 = True          # use the 12 qubit layout for the display
                UseTee = False         # (and give it precedence over the tee display
                UseHex = False
                    
            if '-e' in parameter: UseEmulator = True       # force use of the SenseHat emulator even if hardware is installed
            if '-dual' in parameter: DualDisplay = True
            if '-select' in parameter: 
                SelectBackend = True
                UseLocal = False
            elif ':' in parameter:                         # parse two-component parameters
                print("processing two part parameter ", parameter)
                token = parameter.split(':')[0]            # before the colon is the key
                value = parameter.split(':')[1]            # after the colon is the value
                if '-b' in token: 
                    backendparm = value      # if the key is -b, specify the backend
                    UseLocal = False
                    print("requested backend: ", backendparm, ", UseLocal set ",UseLocal)
                elif '-f' in token:
                    qasmfileinput = value  # if the key is -f, specify the qasm file
                    print("-f option: filename",qasmfileinput)
                elif '-nois' in token: fake_name = value
            if debug: input("press Enter to continue")
             
      
print ("QASM File input",qasmfileinput)


# Now we are going to try to instantiate the SenseHat, unless we have asked for the emulator.
# if it fails, we'll try loading the emulator 
SenseHatEMU = False
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
    from sense_emu import SenseHat         # class for controlling the SenseHat
    hat = SenseHat() # instantiating hat emulator so we can use it in functions
    while not SenseHatEMU:
        try:
            hat.set_imu_config(True,True,True) #initialize the accelerometer simulation
        except:
            sleep(1)
        else:
            SenseHatEMU = True
else:
    if DualDisplay:
        from sense_emu import SenseHat         # class for controlling the SenseHat
        hat2 = SenseHat() # instantiating hat emulator so we can use it in functions
        while not SenseHatEMU:
            try:
                hat2.set_imu_config(True,True,True) #initialize the accelerometer simulation
            except:
                sleep(1)
            else:
                SenseHatEMU = True
    

# some variables and settings we are going to need as we start up

print("Setting up...")
# This (hiding deprecation warnings) is temporary because the libraries are changing again
warnings.filterwarnings("ignore", category=DeprecationWarning) 
Looping = True    # this will be set false after the first go-round if a real backend is called
angle = 180
result = None
runcounter=0
maxpattern='00000'
interval=5
stalled_time = 60 # how many seconds we're willing to wait once a job status is "Running"

thinking=False    # used to tell the display thread when to show the result
shutdown=False    # used to tell the display thread to trigger a shutdown
qdone=False
showlogo=False

###########################################################################################
#-------------------------------------------------------------------------------    
#   These variables and functions are for lighting up the qubit display on the SenseHat
#                 ibm_qx5 builds a "bowtie" 
#           They were moved up here so we can flash a "Q" as soon as the libraries load
#              
#   the color shift effect is based on the rainbow example included with the SenseHat library
#-------------------------------------------------------------------------------

# pixel coordinates to draw the bowtie qubits or the 16 qubit array
ibm_qx5 = [[40,41,48,49],[8,9,16,17],[28,29,36,37],[6,7,14,15],[54,55,62,63]]
ibm_qx5t = [[0,1,8,9],[3,4,11,12],[6,7,14,15],[27,28,35,36],[51,52,59,60]] 
ibm_qhex = [                [3],
                        [10],   [12],
                    [17],            [21],
                [24],                      [30],
                    [33],            [37],
                        [42],   [44],
                            [51] ]
ibm_qx16 = [[63],[54],[61],[52],[59],[50],[57],[48],
            [7],[14],[5],[12],[3],[10],[1],[8]]
            #[[0],[9],[2],[11],[4],[13],[6],[15],
            #[56],[49],[58],[51],[60],[53],[62],[55]]

# global to spell OFF in a single operation
X = [255, 255, 255]  # white
O = [  0,   0,   0]  # black

off = [
   O, O, O, O, O, O, O, O,
   O, X, O, X, X, O, X, X,
   X, O, X, X, O, O, X, O,
   X, O, X, X, X, O, X, X,
   X, O, X, X, O, O, X, O,
   O, X, O, X, O, O, X, O,
   O, O, O, O, O, O, O, O,
   O, O, O, O, O, O, O, O,
   ]

Qlogo = [
   O, O, O, X, X, O, O, O,
   O, O, X, O, O, X, O, O,
   O, O, X, O, O, X, O, O,
   O, O, X, O, O, X, O, O,
   O, O, X, O, O, X, O, O,
   O, O, O, X, X, O, O, O,
   O, O, O, O, X, O, O, O,
   O, O, O, X, X, O, O, O,
   ]


QLarray = [
              [3],[4],
         [10],       [13],
         [18],       [21],
         [26],       [29],
         [34],       [37],
             [43],[44],
                  [52],
             [59],[60]
    ]

QArcs = [
   O, O, O, O, O, O, X, O,
   O, O, O, O, X, X, X, X,
   O, O, X, X, O, O, X, O,
   O, O, X, O, O, O, X, O,
   O, X, O, O, O, X, X, O,
   O, X, O, O, X, X, O, O,
   X, X, X, X, O, O, O, O,
   O, X, O, O, O, O, O, O,
   ]
QArcsArray = [
                            [6]    ,
                  [12],[13],[14],[15],
        [18],[19],          [22], 
        [26],               [30],
    [33],              [37],
    [41],         [44],[45],
   [48],[49],[50],[51],
        [57]
   ]

QKLogo = [
   O, O, X, X, X, X, O, O,
   O, X, X, O, O, X, X, O,
   X, X, X, O, O, X, X, X,
   X, X, O, X, X, O, X, X,
   X, X, O, O, O, O, X, X,
   X, O, X, X, X, X, O, X,
   O, X, O, O, O, O, X, O,
   O, O, X, X, X, X, O, O,
   ]
QKLogo_mask = [
              [2], [3],  [4], [5],
              
         [9],[10],           [13],[14],
         
    [16],[17],[18],          [21],[22],[23], 
    
    [24],[25],     [27],[28],          [31],
    
    [32],[33],                    [38],[39],
    
    [40],     [42],[43], [44],[45],    [47],
   
         [49],                    [54],
         
              [58],[59],[60],[61]
   ]
QHex = [
        O, O, O, X, O, O, O, O,
        O, O, X, O, X, O, O, O,
        O, X, O, O, O, X, O, O,
        X, O, O, O, O, O, X, O,                 
        O, X, O, O, O, X, O, O,
        O, O, X, O, X, O, O, O,
        O, O, O, X, O, O, O, O,
        O, O, O, O, O, O, O, O,
        ]

Arrow = [
   O, O, O, X, O, O, O, O,
   O, O, X, X, X, O, O, O,
   O, X, O, X, O, X, O, O,
   X, O, O, X, O, O, X, O,
   O, O, O, X, O, O, O, O,
   O, O, O, X, O, O, O, O,
   O, O, O, X, O, O, O, O,
   O, O, O, X, O, O, O, O,
   ]

# setting up the 8x8=64 pixel variables for color shifts

hues = [
    0.00, 0.00, 0.06, 0.13, 0.20, 0.27, 0.34, 0.41,
    0.00, 0.06, 0.13, 0.21, 0.28, 0.35, 0.42, 0.49,
    0.07, 0.14, 0.21, 0.28, 0.35, 0.42, 0.50, 0.57,
    0.15, 0.22, 0.29, 0.36, 0.43, 0.50, 0.57, 0.64,
    0.22, 0.29, 0.36, 0.44, 0.51, 0.58, 0.65, 0.72,
    0.30, 0.37, 0.44, 0.51, 0.58, 0.66, 0.73, 0.80,
    0.38, 0.45, 0.52, 0.59, 0.66, 0.73, 0.80, 0.87,
    0.45, 0.52, 0.60, 0.67, 0.74, 0.81, 0.88, 0.95,
    ]

pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]
qubits = pixels

# scale lets us do a simple color rotation of hues and convert it to RGB in pixels

def scale(v):
    return int(v * 255)

def resetrainbow(show=False):
   global pixels,hues
   pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]
   pixels = [(scale(r), scale(g), scale(b)) for r, g, b in pixels]
   if (show):
       hat.set_pixels(pixels)
       if DualDisplay: hat2.set_pixels(pixels)

def showqubits(pattern='0000000000000000'):
   global hat, qubits
   padding=''
   svgpattern=pattern
   if len(pattern)<len(display):
       for x in range(len(display)-len(pattern)):
            padding = padding + '0'
       pattern = pattern + padding
   for p in range(64):          #first set all pixels off
           pixels[p]=[0,0,0]
   for q in range(len(display)):
      if pattern[q]=='1':         # if the digit is "1" assign blue
         for p in display[q]:
            pixels[p]=[0,0,255]
      elif q >= qubits_needed:
         for p in display[q]:    # if outside the number of measured qubits in the circuit, dim purple
            pixels[p]=[75,0,75]
      else:                       # otherwise assign it red
         for p in display[q]:     
            pixels[p]=[255,0,0]
   qubits=pixels
   qubitpattern=pattern
   hat.set_pixels(pixels)         # turn them all on
   write_svg_file(pixels, svgpattern, 2.5, False)
   if DualDisplay: hat2.set_pixels(pixels)
   #write_svg_file(qubits,2.5)
   
#--------------------------------------------------
#    blinky lets us use the rainbow rotation code to fill the bowtie pattern
#       it can be interrupted by tapping the joystick or if
#       an experiment ID is provided and the 
#       status returns "DONE"
#
#------------------------------------------------------

def blinky(time=20,experimentID=''):
   global pixels,hues,experiment, Qlogo, showlogo, QArcs, QKLogo, QHex, qubits, qubitpattern
   if QWhileThinking:
       mask = QKLogo_mask
   else:
       mask = display
   #resetrainbow()
   count=0
   GoNow=False
   while ((count*.02<time) and (not GoNow)):
      # Rotate the hues
      hues = [(h + 0.01) % 1.0 for h in hues]
      # Convert the hues to RGB values
      pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]
      # hsv_to_rgb returns 0..1 floats; convert to ints in the range 0..255
      pixels = [(scale(r), scale(g), scale(b)) for r, g, b in pixels]
      for p in range(64):
         #if QWhileThinking:
         #    if p in sum(Qlogo,[]):
          #       pass
          #   else:
          #       pixels[p]=[0,0,0]
        # else:
             if p in sum(mask,[]):
             #if p in sum(display,[]):
                pass
             else:
                pixels[p]=[0,0,0]
      if (result is not None):
         if (result.status=='COMPLETED'):
            GoNow=True
    # Update the display
      if not showlogo:
          hat.set_pixels(pixels)
          if DualDisplay: hat2.set_pixels(pixels)
      else:
          hat.set_pixels(QKLogo)
          if DualDisplay: hat2.set_pixels(QArcs)
      sleep(0.002)
      count+=1
      for event in hat.stick.get_events():
         if event.action == 'pressed':
            goNow=True
         if event.action == 'held' and event.direction =='middle':
            shutdown=True 


#------------------------------------------------
#  now that the light pattern functions are defined,
#    build a class glow so we can launch display control as a thread
#------------------------------------------------
class glow():
   global thinking,hat, maxpattern, shutdown,off,Qlogo, QArcs, Qhex

   def __init__(self):
      self._running = True
      
   def stop(self):
      self._running = False
      self._stop = True

   def run(self):
      #thinking=False
      while self._running:
         if shutdown:
            hat.set_rotation(angle)
            hat.set_pixels(off)
            sleep(1)
            hat.clear()
            if DualDisplay: hat2.clear()
            path = 'sudo shutdown -P now '
            os.system (path)
         else:
           if thinking:
              blinky(.1)
           else:
              showqubits(maxpattern)


#----------------------------------------------------------------
# Set the display size and rotation Turn on the display with an IBM "Q" logo
#----------------------------------------------------------------
def orient():
    global hat,angle
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
    print("angle selected:",angle)
    

    hat.set_rotation(angle)
    if DualDisplay: hat2.set_rotation(0)

# Now call the orient function and show an arrow

orient()
display=ibm_qx16    
hat.set_pixels(Arrow)
if DualDisplay: hat2.set_pixels(Arrow)



##################################################################
#   Input file functions
##################################################################

#----------------------------------------------------------
# find our experiment file... alternate can be specified on command line
#       use a couple tricks to make sure it is there
#       if not fall back on our default file
#def loadQASMfile():

scriptfolder = os.path.dirname(os.path.realpath("__file__"))
#print(sys.argv)
#print ("Number of arguments: ",len(sys.argv))
# look for a filename option
#if (len(sys.argv) > 1) and type(sys.argv[1]) is str:
  #print (type(sys.argv[1]))
 # qasmfilename=sys.argv[1]
#  print ("input arg:",qasmfilename)
if (qasmfileinput == '16'):    qasmfilename='expt16.qasm' 
else: qasmfilename = qasmfileinput
  #qasmfilename='expt.qasm'
print("QASM File:",qasmfilename)

#complete the path if necessary
if ('/' not in qasmfilename):
  qasmfilename=scriptfolder+"/"+qasmfilename
if (not os.path.isfile(qasmfilename)):
    qasmfilename=scriptfolder+"/"+'expt.qasm'
    
print("OPENQASM file: ",qasmfilename)
if (not os.path.isfile(qasmfilename)):
    print("QASM file not found... exiting.")
    exit()
    
# Parse any other parameters:



# end DEF ----------------------

###############################################################
#   Connection functions
#       ping and authentication
###############################################################

#----------------------------------------------------------------------------
# set up a ping function so we can confirm the service can connect before we attempt it
#           ping uses the requests library
#           based on pi-ping by Wesley Archer (raspberrycoulis) (c) 2017
#           https://github.com/raspberrycoulis/Pi-Ping
#----------------------------------------------------------------------------
def ping(website='https://quantum-computing.ibm.com/',repeats=1,wait=0.5,verbose=False):
  msg = 'ping response'
  for n in range(repeats):
    response = requests.get(website)
    if int(response.status_code) == 200: # OK
        pass
    elif int(response.status_code) == 500: # Internal server error
        msg ='Internal server error'
    elif int(response.status_code) == 503: # Service unavailable
        msg = 'Service unavailable'
    elif int(response.status_code) == 502: # Bad gateway
        msg = 'Bad gateway'
    elif int(response.status_code) == 520: # Cloudflare: Unknown error
        msg = 'Cloudflare: Unknown error'
    elif int(response.status_code) == 522: # Cloudflare: Connection timed out
        msg = 'Cloudflare: Connection timed out'
    elif int(response.status_code) == 523: # Cloudflare: Origin is unreachable
        msg = 'Cloudflare: Origin is unreachable'
    elif int(response.status_code) == 524: # Cloudflare: A Timeout occurred
        msg = 'Cloudflare: A Timeout occurred'
    if verbose: print(response.status_code,msg)
    if repeats>1: sleep(wait)
    
  return int(response.status_code)
# end DEF ----------------------------------------------------------------




# ------------------------------------------------------------------------
#  try to start our IBM Quantum backend (simulator or real) and connection to IBM Quantum APIs
#       Here we attempt to ping the IBM Quantum Computing API servers. If no response, we exit
#       If we get a 200 response, the site is live and we initialize our connection to it
#-------------------------------------------------------------------------------
def startIBMQ():
    global Q, backend, UseLocal, backendparm
    # This version written to work only with the new QiskitRuntimeService module from Qiskit > v1.0
    sQPV = IBMQVersion
    pd = '.'
    dot1 = [pos for pos, char in enumerate(sQPV) if char==pd][0]
    dot2 = [pos for pos, char in enumerate(sQPV) if char==pd][1]
    IBMQP_Vers=float(sQPV[0:dot2])
    if SelectBackend:
        backendparm = input("type the backend you wish to use:\n"
                            "'least' will find a least-busy real backend.\n"
                            " 'aer' will generate a basic Aer Simulator\n"
                            " 'aernois' or 'airmodel' will create a real-system noise modeled Aer simulator.\n")
    elif UseLocal: backendparm = "FakeManilaV2"                        
    print('IBMQ Provider v',IBMQP_Vers, "backendparm ",backendparm,", UseLocal",UseLocal)
    if debug: input("Press Enter Key")
    if qubits_needed > 5 and UseLocal: 
        UseLocal = False
        backendparm = 'aer'
            
    if not UseLocal:
            
        print ('Pinging IBM Quantum API server before start')
        p=ping('https://api.quantum-computing.ibm.com',1,0.5,True)
        #p=ping('https://auth.quantum-computing.ibm.com/api',1,0.5,True)
        #p=ping('https://quantum-computing.ibm.com/',1,0.5,True)
        try:
            print("requested backend: ",backendparm)
        except:
            sleep(0)
        
        # specify the simulator as the backup backend (this must change after May 15 2024)
        backend='ibmq_qasm_simulator'   
        if p==200:
            if (IBMQP_Vers >= 1):   # The new authentication technique with provider as the object
                print("trying to create backend connection")
                Qservice=QiskitRuntimeService()
                if "aer" in backendparm:
                    from qiskit_aer import AerSimulator
                    if "model" in backendparm or "nois" in backendparm or AddNoise:
                        print("getting a real backend connection for aer model")
                        real_backend = Qservice.least_busy(simulator=False)#operational=True, backend("ibm_brisbane")
                        print("creating AerSimulator modeled from ",real_backend.name)
                        Q = AerSimulator.from_backend(real_backend)
                    else:
                        print("creating basic Aer Simulator")
                        Q = AerSimulator()    
                    UseLocal=True  #now that it's built, mark the backend as local
                else:
                    try:
                        if "least" in backendparm:
                            Q = Qservice.least_busy(operational=True, simulator=False)
                        else:
                            Q = Qservice.backend(backendparm)
                            
                    except:
                        print("first backend attempt failed...")
                        Q=Qservice.backend(backend)
                    else:
                        interval = 300
            else:                    # The older IBMQ authentication technique
                exit() #this code only works with the new Qiskit>v1.0
        else:
            exit()
    else: # THIS IS THE CASE FOR USING LOCAL SIMULATOR
        backend='local aer qasm_simulator'
        print ("Building ",backend, "with requested attributes...")
        if not AddNoise:
            from qiskit_aer import AerSimulator
            Q = AerSimulator()  #Aer.get_backend('qasm_simulator')
        else:
            Q = FakeManilaV2() 
#-------------------------------------------------------------------------------


#################################################################################
#
#   Main program loop  (note: we turned on a logo earlier at line 202)
#
#################################################################################



# Instantiate an instance of our glow class
print("Instantiating glow...")
glowing = glow()
# create the html shell file
write_svg_file(pixels, maxpattern, 2.5, True)
#-------------------------------------------------
#  OK, let's get this shindig started
#-------------------------------------------------
#First, let's read our input file and see how many qubits we need?
 
exptfile = open(qasmfilename,'r') # open the file with the OPENQASM code in it
qasm= exptfile.read()            # read the contents into our experiment string

if (len(qasm)<5):                # if that is too short to be real, exit
    exit
else:                            # otherwise print it to the console for reference
    print("OPENQASM code to send:\n",qasm)

#to determin the number of qubits, we have to make the circuit
    
qcirc=QuantumCircuit.from_qasm_str(qasm)   
qubits_needed = qcirc.num_qubits

rainbowTie = Thread(target=glowing.run)     # create the display thread
startIBMQ()                                  # try to connect and instantiate the IBMQ 

qcirc=QuantumCircuit.from_qasm_str(qasm)   
try:
    print("generating circuit from QASM")# (qcirc)
except UnicodeEncodeError:
    print ('Unable to render quantum circuit drawing; incompatible Unicode environment')
except:
    print ('Unable to render quantum circuit drawing for some reason')
    
if (qubits_needed > 5 and not UseHex) or UseQ16:
    display = ibm_qx16
    maxpattern='0000000000000000'
    print ("circuit width: ",qubits_needed," using 16 qubit display")
else:
    if (UseTee and qubits_needed <= 5 ): 
        display = ibm_qx5t
        maxpattern='00000'
    elif (UseHex): 
        display = ibm_qhex
        maxpattern='000000000000'
    else: 
        display = ibm_qx5
        maxpattern='00000'
    
    print ("circuit width: ",qubits_needed," using 5 qubit display")
qubitpattern=maxpattern
#backend='simulator' 
rainbowTie.start()                          # start the display thread


while Looping:
   runcounter += 1
   if "aer" in backendparm: UseLocal=True
   try:
       if not UseLocal:
           p=ping()
       else:
           p=200
   except:
       print("connection problem with IBMQ")
   else:
       if p==200:
           orient()
           showlogo = True
           thinking = True
           Qname=Q.name
           print("Name:",Q.name,"Version:",Q.version,"No. of qubits:",Q.num_qubits)
           if not UseLocal and not "aer" in backendparm: 
               Qstatus=Q.status()
               print(Qstatus.backend_name, "is simulator? ", Q.simulator, "| operational: ", Qstatus.operational ,"|  jobs in queue:",Qstatus.pending_jobs)

           try:
               if not UseLocal:
                    Qstatus = Q.status()  # check the availability
           except:
               print('Problem getting backend status... waiting to try again')
           else:
               if not UseLocal: 
                    Qstatus=Q.status()                
                    print('Backend Status: ',Qstatus.status_msg, 'operational:',Qstatus.operational)
                    if debug: input('press enter')
                    qstatmsg=Qstatus.status_msg
                    q_operational=Qstatus.operational
               else:
                    qstatmsg='active'
                    q_operational=False
               if (qstatmsg == 'active' and q_operational)  or UseLocal:
                   
                   print('     executing quantum circuit... on ',Q.name)
                   #print(Q.name,' options:',Q.options)
                   try:
                        print (qcirc)
                   except UnicodeEncodeError:
                        print ('Unable to render quantum circuit drawing; incompatible Unicode environment')
                   except:
                        print ('Unable to render quantum circuit drawing for some reason')
                   try:
                        qk1_circ=transpile(qcirc, Q) # transpile for the new primitive
                   except:
                        print("problem transpiling circuit")
                   else:
                        print("transpilation complete")                    
                   #try:
                        if not UseLocal:
                            print("backend: ",Q.name," operational? ",Q.status().operational," Pending:",Q.status().pending_jobs)
                        else:
                            print("backend: ",Q.name," operational? ALWAYS")
                        if debug: input('Press the Enter Key')
                        print("running job")                       
                        qjob=Q.run(qk1_circ) # run 
                        print("JobID: ",qjob.job_id())
                        print("Job Done?",qjob.done())
                        #if qjob.errored():
                        #   print("error message:",qjob.error_message())
                        #qjob=execute(qcirc, Q, shots=500, memory=False)
                        Looping =  UseLocal or Q.simulator
                        if runcounter < 3: print("Using ", Qname, " ... Looping is set ", Looping)
                   
                        running_start = 0
                        running_timeout = False
                        running_cancelled = False
                        showlogo =  False
                        qdone = False
                        while not (qdone or running_timeout or running_cancelled):
                            qdone = qjob.in_final_state() or qjob.cancelled()
                            if not UseLocal:
                                print(running_start,qjob.job_id(),"Job Done? ", qjob.in_final_state(),"| Cancelled? ",qjob.cancelled(),"| queued jobs:",qjob.backend().status().pending_jobs)
                            else:
                                print(running_start,qjob.job_id(),"Job Done? ", qjob.in_final_state(),"| Cancelled? ",qjob.cancelled())
                            if not qdone: running_start+=1;
                            #if qjob.errored():
                             #  print("error message:",qjob.error_message())
                              # running_cancelled = True                              
                        if qjob.done() :
                           # only get here once we get DONE status
                           result=qjob.result()     # get the result
                           counts=result.get_counts(qcirc)   
                           #print("counts:",counts)
                           maxpattern=max(counts,key=counts.get)
                           qubitpattern=maxpattern
                           maxvalue=counts[maxpattern]
                           print("Maximum value:",maxvalue, "Maximum pattern:",maxpattern)
                           if UseLocal:
                               sleep(3)
                           thinking = False  # this cues the display thread to show the qubits in maxpattern
                        if running_timeout :
                            print(backend,' Queue appears to have stalled. Restarting Job.')
                        if running_cancelled :
                            print(backend,' Job cancelled at backend. Restarting.')    
                   #except:
                    #    print(Q.name, qjob.job_id(), 'problem; waiting to try again')
       #else:
        #   print(p,'response to ping; waiting to try again')
   #print("qubit list",qubits)
   #write_svg_file(qubits,maxpattern, 2.5)
   goAgain=False                    # wait to do it again
   if Looping: print('Waiting ',interval,'s before next run...')
   
   myTimer=process_time()
   while not goAgain:
      for event in hat.stick.get_events():   
         if event.action == 'pressed':      #somebody tapped the joystick -- go now
            goAgain=True
            blinky(.001)
            hat.set_pixels(pixels)
            if DualDisplay: hat2.set_pixels(pixels)
         if event.action == 'held' and event.direction =='middle':
            shutdown=True 
         if event.action == 'held' and event.direction !='middle':
             Looping = False
             break
      if (process_time()-myTimer>interval):       # 10 seconds elapsed -- go now
            goAgain=True

print("Program Execution ended normally")
