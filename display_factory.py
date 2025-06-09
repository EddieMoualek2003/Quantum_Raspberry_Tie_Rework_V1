# display_factory.py

from emulator_display import EmulatorDisplay
# from sensehat_display import SenseHatDisplay
from svg_display import SVGDisplay

def display_factory(use_emulator=True, use_sensehat=False, use_svg=False):
    if use_emulator:
        return EmulatorDisplay()
    elif use_svg:
        return SVGDisplay()
    else:
        raise RuntimeError("No valid display type selected.")