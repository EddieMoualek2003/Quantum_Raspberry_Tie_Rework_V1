# sensehat_display.py

from display import Display
from sense_hat import SenseHat
from colorsys import hsv_to_rgb
from time import sleep

class SenseHatDisplay(Display):
    """Physical SenseHat display."""

    # These are the qubit layout positions from the original code
    IBM_QX5 = [[40,41,48,49], [8,9,16,17], [28,29,36,37], [6,7,14,15], [54,55,62,63]]

    def __init__(self, config=None):
        super().__init__(config)
        self.hat = SenseHat()
        self.hat.low_light = True
        self.angle = 180  # Default rotation
        self.display_map = self.IBM_QX5  # Default layout
        self.pixels = [(0, 0, 0)] * 64  # 8x8 display

    def initialize(self):
        """Initialize orientation."""
        self._set_orientation()

    def _set_orientation(self):
        """Read accelerometer and set rotation angle accordingly."""
        acceleration = self.hat.get_accelerometer_raw()
        x = round(acceleration['x'], 0)
        y = round(acceleration['y'], 0)

        if y == -1:
            self.angle = 180
        elif y == 1:
            self.angle = 0
        elif x == -1:
            self.angle = 90
        elif x == 1:
            self.angle = 270

        self.hat.set_rotation(self.angle)

    def set_pixels(self, pixel_list):
        """Directly set all 64 pixels."""
        if len(pixel_list) != 64:
            raise ValueError("Expected 64 RGB pixels")
        self.hat.set_pixels(pixel_list)

    def show_qubits(self, bit_pattern: str):
        """Map a binary string to the current display layout (default: IBM_QX5)."""
        pattern = bit_pattern.zfill(len(self.display_map))  # pad to length
        pixels = [(0, 0, 0)] * 64  # start with everything off

        for i, bit in enumerate(pattern):
            for pos in self.display_map[i]:
                if bit == '1':
                    pixels[pos] = (0, 0, 255)  # blue
                else:
                    pixels[pos] = (255, 0, 0)  # red

        self.set_pixels(pixels)

    def blinky(self, duration=2):
        """Rainbow hue cycling on qubit locations."""
        hues = [(i / 64) for i in range(64)]

        for _ in range(int(duration * 50)):
            hues = [(h + 0.01) % 1.0 for h in hues]
            pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]
            pixels = [(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in pixels]

            # Only show qubit positions, blank the rest
            filtered = [(0, 0, 0)] * 64
            for group in self.display_map:
                for p in group:
                    filtered[p] = pixels[p]

            self.set_pixels(filtered)
    def clear(self):
        """Clear the Sense HAT display."""
        self.hat.clear()

