# emulator_display.py

from display import Display
from sense_emu import SenseHat
from colorsys import hsv_to_rgb
from time import sleep

class EmulatorDisplay(Display):
    """SenseHat emulator-based display. Fully standalone."""

    IBM_QX5 = [[40,41,48,49], [8,9,16,17], [28,29,36,37], [6,7,14,15], [54,55,62,63]]

    def __init__(self, config=None):
        super().__init__(config)
        self.hat = SenseHat()
        self.max_wait = 10
        self.angle = 180
        self.display_map = self.IBM_QX5
        self.pixels = [(0, 0, 0)] * 64

    def initialize(self):
        """Wait for emulator to be ready and set display rotation."""
        print("Waiting for SenseHat emulator to start...")
        ready = False
        for i in range(self.max_wait):
            try:
                self.hat.set_imu_config(True, True, True)
                ready = True
                break
            except Exception:
                sleep(1)

        if not ready:
            raise RuntimeError("SenseHat emulator not detected. Is it running?")
        
        self._set_orientation()
        print("Emulator ready with angle:", self.angle)

    def _set_orientation(self):
        """Set rotation based on dummy accelerometer data."""
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
        if len(pixel_list) != 64:
            raise ValueError("Expected 64 RGB tuples for SenseHat display.")
        self.pixels = pixel_list
        self.hat.set_pixels(self.pixels)

    def show_qubits(self, bit_pattern: str):
        """Map a bitstring to colored qubit pixels."""
        pattern = bit_pattern.zfill(len(self.display_map))
        pixels = [(0, 0, 0)] * 64  # clear background

        for i, bit in enumerate(pattern):
            for pos in self.display_map[i]:
                if bit == '1':
                    pixels[pos] = (0, 0, 255)  # Blue = 1
                else:
                    pixels[pos] = (255, 0, 0)  # Red = 0

        self.set_pixels(pixels)

    def blinky(self, duration=2):
        """Animate a rainbow swirl on the qubit positions."""
        hues = [(i / 64) for i in range(64)]

        for _ in range(int(duration * 50)):
            hues = [(h + 0.01) % 1.0 for h in hues]
            pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]
            pixels = [(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in pixels]

            filtered = [(0, 0, 0)] * 64
            for group in self.display_map:
                for p in group:
                    filtered[p] = pixels[p]

            self.set_pixels(filtered)
            sleep(0.02)

    def clear(self):
        """Clear the emulator display."""
        self.hat.clear()
