from OSTBCEnums import ModulationType
import numpy as np
import GlobalSettings
import matplotlib.pyplot as plot

class InvalidModulationScheme(Exception):
    pass

class NonBinaryInput(Exception):
    pass

class Transmitter():
    def __init__(self, carrierFreq = GlobalSettings.carrierFrequency):
        self.fc = carrierFreq
        
    def Modulate(self, inputData, modulationScheme, messageFreq = GlobalSettings.messageFrequency, transmitPower = 0.5):
        if(modulationScheme == ModulationType.BPSK):
            binData = list(inputData) #Converts to list of '1's and '0's
            messageTime = 1/messageFreq
            numBits = len(binData)
            a = np.sqrt(2*transmitPower)
            output = []
            for x in range(numBits):
                bitTransmitTime = np.arange(x*messageTime,(x*messageTime) + messageTime,GlobalSettings.sampleTime)
                if binData[x] == '1':
                    output.extend(a*np.cos(2*np.pi*self.fc*bitTransmitTime))
                elif binData[x] == '0':
                    output.extend(-a*np.cos(2*np.pi*self.fc*bitTransmitTime))
                else:
                    raise NonBinaryInput()
            return output
        elif(modulationScheme == ModulationType.QAM16):
            return 0
        elif(modulationScheme == ModulationType.QAM64):
            return 0
        else:
            raise InvalidModulationScheme()
    
#Test for Class
transmitter = Transmitter()
binSequence = '0'
modulated = transmitter.Modulate(binSequence,ModulationType.BPSK)
plot.plot(modulated)
