# main.py

from display_factory import display_factory
from quantum_experiment import QuantumExperiment
from time import sleep


def main():
    print("Starting Quantum Raspberry Tie Demo")

    # --- Choose display type here ---
    # display = display_factory(use_emulator=True)
    display = display_factory(use_svg=True)
    display.initialize()

    # --- Set up quantum experiment ---
    experiment = QuantumExperiment(
        qasm_path="expt.qasm",
        use_local=True,
        backend_name="FakeManilaV2"  # or "aer"
    )

    try:
        experiment.load_qasm()
        experiment.select_backend()

        print("Running quantum job...")
        display.blinky(duration=3)
        experiment.run()

        result_pattern = experiment.get_max_pattern()
        print("Most common result:", result_pattern)

        print("Displaying result on emulator...")
        display.show_qubits(result_pattern)
        sleep(3)

    finally:
        print("Clearing display.")
        display.clear()


if __name__ == "__main__":
    main()
