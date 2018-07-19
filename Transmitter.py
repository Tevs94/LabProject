from OSTBCEnums import ModulationType

class InvalidModulationScheme():
    pass

class Transmitter():
    def __init__(self, carrierFrequency):
        self.fc = carrierFrequency
        
    def Modulate(self, inputData, modulationScheme):
        if(modulationScheme == ModulationType.BPSK):
            return 0
        elif(modulationScheme == ModulationType.QAM16):
            return 0
        elif(modulationScheme == ModulationType.QAM64):
            return 0
        else:
            raise InvalidModulationScheme()
    
            

        