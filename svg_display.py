# svg_display.py

from display import Display
import os

class SVGDisplay(Display):
    def __init__(self, config=None):
        super().__init__(config)
        self.display_map = [
            [40,41,48,49],
            [8,9,16,17],
            [28,29,36,37],
            [6,7,14,15],
            [54,55,62,63]
        ]
        self.pixels = [(0, 0, 0)] * 64
        self.output_dir = "./svg"

    def initialize(self):
        os.makedirs(self.output_dir, exist_ok=True)
        self._write_html_shell()
        print("SVG display initialized.")

    def _write_html_shell(self):
        html_path = os.path.join(self.output_dir, "qubits.html")
        with open(html_path, "w") as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Qubit Display</title>
    <meta http-equiv="refresh" content="2">
</head>
<body>
    <h3>Latest Qubit Display</h3>
    <object data="pixels.svg" type="image/svg+xml" width="400" height="400"></object>
</body>
</html>''')

    def _rgb_to_hex(self, r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    def _generate_svg(self, pixel_list):
        svg = ['<svg width="128" height="128" xmlns="http://www.w3.org/2000/svg">']
        for i in range(64):
            x = (i % 8) * 16
            y = (i // 8) * 16
            r, g, b = pixel_list[i]
            color = self._rgb_to_hex(r, g, b)
            svg.append(f'<rect x="{x}" y="{y}" width="16" height="16" fill="{color}" stroke="black"/>')
        svg.append('</svg>')
        return "\n".join(svg)

    def set_pixels(self, pixel_list):
        self.pixels = pixel_list
        svg_code = self._generate_svg(pixel_list)
        with open(os.path.join(self.output_dir, "pixels.svg"), "w") as f:
            f.write(svg_code)

    def show_qubits(self, bit_pattern: str):
        pattern = bit_pattern.zfill(len(self.display_map))
        pixels = [(0, 0, 0)] * 64

        for i, bit in enumerate(pattern):
            for pos in self.display_map[i]:
                if bit == '1':
                    pixels[pos] = (0, 0, 255)
                else:
                    pixels[pos] = (255, 0, 0)

        self.set_pixels(pixels)

    def blinky(self, duration=2):
        # For simplicity, simulate a static rainbow pattern
        import colorsys
        from time import sleep

        hues = [(i / 64.0) for i in range(64)]
        pixels = [
            tuple(int(x * 255) for x in colorsys.hsv_to_rgb(h, 1.0, 1.0))
            for h in hues
        ]
        self.set_pixels(pixels)
        sleep(duration)

    def clear(self):
        self.set_pixels([(0, 0, 0)] * 64)
        print("SVG display cleared.")
