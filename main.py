# from display_factory import display_factory

# display = display_factory(use_emulator=True)
# display.initialize()
# display.blinky(2)
# display.show_qubits("11010")

from quantum_experiment import QuantumExperiment

experiment = QuantumExperiment("expt.qasm", use_local=True)
experiment.load_qasm()
experiment.select_backend()
experiment.run()
pattern = experiment.get_max_pattern()
print("Most common result:", pattern)
