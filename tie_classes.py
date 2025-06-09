# display.py

from abc import ABC, abstractmethod

class Display(ABC):
    """Abstract base class for a quantum display device."""

    def __init__(self, config=None):
        self.config = config

    @abstractmethod
    def initialize(self):
        """Initialize the display device."""
        pass

    @abstractmethod
    def set_pixels(self, pixel_list):
        """Set the full display to an array of RGB tuples."""
        pass

    @abstractmethod
    def show_qubits(self, bit_pattern: str):
        """Display a binary qubit pattern like '10101' on the physical layout."""
        pass

    @abstractmethod
    def blinky(self, duration=2):
        """Optional animated rainbow effect while thinking."""
        pass

    @abstractmethod
    def clear(self):
        """Clear or turn off the display."""
        pass
