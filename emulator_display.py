# emulator_display.py

from sensehat_display import SenseHatDisplay
from sense_emu import SenseHat
from time import sleep

class EmulatorDisplay(SenseHatDisplay):
    """SenseHat emulator-based display (same interface as hardware)."""

    def __init__(self, config=None):
        # Override: use sense_emu instead of sense_hat
        super().__init__(config)
        self.hat = SenseHat()
        self.max_wait = 10  # seconds to wait for emulator

    def initialize(self):
        """Wait for emulator to be ready and set orientation."""
        print("Waiting for SenseHat emulator to start...")
        ready = False
        for i in range(self.max_wait):
            try:
                # Trigger a method to check if emulator is active
                self.hat.set_imu_config(True, True, True)
                ready = True
                break
            except Exception:
                sleep(1)

        if not ready:
            raise RuntimeError("SenseHat emulator not detected. Is it running?")

        print("SenseHat emulator ready.")
        self._set_orientation()
