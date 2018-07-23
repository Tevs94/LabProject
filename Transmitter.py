from OSTBCEnums import ModulationType
import numpy as np
import GlobalSettings
import matplotlib.pyplot as plot

class InvalidModulationScheme(Exception):
    pass

class NonBinaryInput(Exception):
    pass

class InputRequiresPadding(Exception):
    pass

class Transmitter():
    def __init__(self, carrierFreq = GlobalSettings.carrierFrequency):
        self.fc = carrierFreq
    
    def Modulate(self, inputData, modulationScheme, messageFreq = GlobalSettings.messageFrequency, transmitPower = 0.5):
        #Constellations: http://weibeld.net/mobcom/psk-qam-modulation.html
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
        
        elif(modulationScheme == ModulationType.QPSK):
            #also known as 4QAM
            binData = list(inputData)
            try:
                messageTime = 1/messageFreq
                numBits = len(binData)
                a = np.sqrt(2*transmitPower)
                output = []
                iqDictionary = {
                       '00': [-a,-a],
                       '01': [-a,a],
                       '10': [a,-a],
                       '11': [a,a],
                }
                for x in range(numBits/2):
                    bitTransmitTime = np.arange(x*messageTime,(x*messageTime) + messageTime,GlobalSettings.sampleTime)
                    bitsToTransmit = binData[2*x]+binData[(2*x)+1]
                    i = iqDictionary.get(bitsToTransmit)[0]
                    q = iqDictionary.get(bitsToTransmit)[1]
                    output.extend(i*np.cos(2*np.pi*self.fc*bitTransmitTime) + q*np.sin(2*np.pi*self.fc*bitTransmitTime))
            except(KeyError):
                raise NonBinaryInput()
            except(IndexError):
                raise InputRequiresPadding()
            return output

        elif(modulationScheme == ModulationType.QAM16):
            binData = list(inputData)
            try:
                messageTime = 1/messageFreq
                numBits = len(binData)
                a = np.sqrt(2*transmitPower)
                output = []
                iqDictionary = {
                       '0000': [-3*a,3*a],
                       '0001': [-3*a,a],
                       '0010': [-3*a,-3*a],
                       '0011': [-3*a,-a],
                       '0100': [-a,3*a],
                       '0101': [-a,a],
                       '0110': [-a,-3*a],
                       '0111': [-a,-a],
                       '1000': [3*a,3*a],
                       '1001': [3*a,a],
                       '1010': [3*a,-3*a],
                       '1011': [3*a,-a],
                       '1100': [a,3*a],
                       '1101': [a,a],
                       '1110': [a,-3*a],
                       '1111': [a,-a],
                }
                for x in range(numBits/4):
                    bitTransmitTime = np.arange(x*messageTime,(x*messageTime) + messageTime,GlobalSettings.sampleTime)
                    bitsToTransmit = binData[4*x]+binData[(4*x)+1]+binData[(4*x)+2]+binData[(4*x)+3]
                    i = iqDictionary.get(bitsToTransmit)[0]
                    q = iqDictionary.get(bitsToTransmit)[1]
                    output.extend(i*np.cos(2*np.pi*self.fc*bitTransmitTime) + q*np.sin(2*np.pi*self.fc*bitTransmitTime))
            except(KeyError):
                raise NonBinaryInput()
            except(IndexError):
                raise InputRequiresPadding()
            return output

        elif(modulationScheme == ModulationType.QAM64):
            binData = list(inputData)
            try:
                messageTime = 1/messageFreq
                numBits = len(binData)
                a = np.sqrt(2*transmitPower)
                output = []
                iqDictionary = {
                       '000000': [-7*a,-7*a],
                       '000001': [-7*a,-5*a],
                       '000010': [-7*a,-1*a],
                       '000011': [-7*a,-3*a],
                       '000100': [-7*a,7*a],
                       '000101': [-7*a,5*a],
                       '000110': [-7*a,1*a],
                       '000111': [-7*a,3*a],
                       '001000': [-5*a,-7*a],
                       '001001': [-5*a,-5*a],
                       '001010': [-5*a,-1*a],
                       '001011': [-5*a,-3*a],
                       '001100': [-5*a,7*a],
                       '001101': [-5*a,5*a],
                       '001110': [-5*a,1*a],
                       '001111': [-5*a,3*a],
                       
                       '010000': [-1*a,-7*a],
                       '010001': [-1*a,-5*a],
                       '010010': [-1*a,-1*a],
                       '010011': [-1*a,-3*a],
                       '010100': [-1*a,7*a],
                       '010101': [-1*a,5*a],
                       '010110': [-1*a,1*a],
                       '010111': [-1*a,3*a],
                       '011000': [-3*a,-7*a],
                       '011001': [-3*a,-5*a],
                       '011010': [-3*a,-1*a],
                       '011011': [-3*a,-3*a],
                       '011100': [-3*a,7*a],
                       '011101': [-3*a,5*a],
                       '011110': [-3*a,1*a],
                       '011111': [-3*a,3*a],
                       
                       '100000': [7*a,-7*a],
                       '100001': [7*a,-5*a],
                       '100010': [7*a,-1*a],
                       '100011': [7*a,-3*a],
                       '100100': [7*a,7*a],
                       '100101': [7*a,5*a],
                       '100110': [7*a,1*a],
                       '100111': [7*a,3*a],
                       '101000': [5*a,-7*a],
                       '101001': [5*a,-5*a],
                       '101010': [5*a,-1*a],
                       '101011': [5*a,-3*a],
                       '101100': [5*a,7*a],
                       '101101': [5*a,5*a],
                       '101110': [5*a,1*a],
                       '101111': [5*a,3*a],
                       
                       '110000': [1*a,-7*a],
                       '110001': [1*a,-5*a],
                       '110010': [1*a,-1*a],
                       '110011': [1*a,-3*a],
                       '110100': [1*a,7*a],
                       '110101': [1*a,5*a],
                       '110110': [1*a,1*a],
                       '110111': [1*a,3*a],
                       '111000': [3*a,-7*a],
                       '111001': [3*a,-5*a],
                       '111010': [3*a,-1*a],
                       '111011': [3*a,-3*a],
                       '111100': [3*a,7*a],
                       '111101': [3*a,5*a],
                       '111110': [3*a,1*a],
                       '111111': [3*a,3*a],
                }
                for x in range(numBits/6):
                    bitTransmitTime = np.arange(x*messageTime,(x*messageTime) + messageTime,GlobalSettings.sampleTime)
                    bitsToTransmit = binData[6*x]+binData[(6*x)+1]+binData[(6*x)+2]+binData[(6*x)+3]+binData[(6*x)+4]+binData[(6*x)+5]
                    i = iqDictionary.get(bitsToTransmit)[0]
                    q = iqDictionary.get(bitsToTransmit)[1]
                    output.extend(i*np.cos(2*np.pi*self.fc*bitTransmitTime) + q*np.sin(2*np.pi*self.fc*bitTransmitTime))
            except(KeyError):
                raise NonBinaryInput()
            except(IndexError):
                raise InputRequiresPadding()
            return output

        else:
            raise InvalidModulationScheme()
    
#Test for Class
transmitter = Transmitter()
binSequence = '010011111111100100'
modulated = transmitter.Modulate(binSequence,ModulationType.QAM64)
plot.plot(modulated)
