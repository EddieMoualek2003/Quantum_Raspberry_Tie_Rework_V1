from display_factory import display_factory

display = display_factory(use_emulator=True)
display.initialize()
display.blinky(2)
display.show_qubits("11010")
