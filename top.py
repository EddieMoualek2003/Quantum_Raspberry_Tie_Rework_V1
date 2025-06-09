from emulator_display import EmulatorDisplay
from time import sleep

if __name__ == "__main__":
    display = EmulatorDisplay()
    display.initialize()

    try:
        display.blinky(3)
        display.show_qubits("10101")
        sleep(2)
    finally:
        display.clear()