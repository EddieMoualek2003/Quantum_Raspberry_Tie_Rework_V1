# quantum_experiment.py

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from qiskit_aer import AerSimulator

import os

class QuantumExperiment:
    def __init__(self, qasm_path="expt.qasm", use_local=True, backend_name="FakeManilaV2"):
        self.qasm_path = qasm_path
        self.use_local = use_local
        self.backend_name = backend_name
        self.backend = None
        self.qasm_code = ""
        self.circuit = None
        self.result = None

    def load_qasm(self):
        if not os.path.isfile(self.qasm_path):
            raise FileNotFoundError(f"QASM file '{self.qasm_path}' not found.")

        with open(self.qasm_path, 'r') as f:
            self.qasm_code = f.read()

        self.circuit = QuantumCircuit.from_qasm_str(self.qasm_code)
        print("QASM loaded and circuit constructed.")

    def select_backend(self):
        if self.use_local:
            if self.backend_name.lower() == "aer":
                self.backend = AerSimulator()
            else:
                self.backend = FakeManilaV2()
        else:
            service = QiskitRuntimeService()
            if self.backend_name == "least":
                self.backend = service.least_busy(simulator=False)
            else:
                self.backend = service.backend(self.backend_name)

        print(f"Using backend: {self.backend.name}")

    def run(self):
        if self.backend is None:
            raise RuntimeError("Backend not initialized.")

        transpiled = transpile(self.circuit, self.backend)

        if self.use_local:
            job = self.backend.run(transpiled)
            self.result = job.result()
        else:
            sampler = Sampler(backend=self.backend)
            self.result = sampler.run(self.circuit).result()

        print("Quantum job completed.")

    def get_counts(self):
        if self.result is None:
            raise RuntimeError("No result available. Run the experiment first.")

        return self.result.get_counts(self.circuit)

    def get_max_pattern(self):
        counts = self.get_counts()
        return max(counts, key=counts.get)
