def return_docstring():
    """
    #----------------------------------------------------------------------
#     QuantumRaspberryTie.qk1_local
#       by KPRoche (Kevin P. Roche) (c) 2017,2018,2019,2020,2021,2022.2024
#
#
#   =============== January 2025 Updates ================================================
#
#   Adding support to display results on a NeoPixel array, either the tiled 8x24 array of the Rasqberry Two
#       or a single BTF 8x32 array
#
#   New Flags for the input line:
#       -notile tells the neopixel code to use a continuous neopixel array map rather than the Rasqberry tiled map
#
#   New behavior: if neither a SenseHat nor a Sensehat emulator are detected, sets a NoHat flag and skips that code
#
#
# ---------------------  November 2024 Update
#      
#     Interactive dialog prompt "-int" added to set up parameters
#       Added to optimize running automatically on Rasqberry Pi System Two
#
#
#
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
    """