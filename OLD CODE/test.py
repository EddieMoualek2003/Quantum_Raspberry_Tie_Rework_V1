class hat_object():
    def __init__(self):
        self.hat = None
        self.hat2 = None

# These are likely to be set at run time, so can be attributes of the quantum object.
class quantum_object():
    def __init__(self):
        self.backendparm = '[localsim]'
        self.SelectBackend = False #for interactive selection of backend
        self.fake_name = "FakeManilaV2"
        self.qubits_needed = 5  #default size for the five-qubit simulation
        self.AddNoise = False
        self.debug = False
        self.qasmfileinput='expt.qasm'