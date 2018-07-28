from OSTBCEnums import ModulationType
import numpy as np
import GlobalSettings
import matplotlib.pyplot as plot
from Transmission import Transmission

class InvalidModulationScheme(Exception):
    pass

class IncorrectBitsToCreateSymbol(Exception):
    pass

class NonBinaryInput(Exception):
    pass

class InputRequiresPadding(Exception):
    pass

class Transmitter():
     #Constellations: http://weibeld.net/mobcom/psk-qam-modulation.html
    def __init__(self, carrierFreq = GlobalSettings.carrierFrequency):
        self.fc = carrierFreq
        
    def GetBitsPerSymbol(self,modulationScheme):
        if(modulationScheme == ModulationType.BPSK):
            return 1
        elif(modulationScheme == ModulationType.QPSK):
            return 2
        elif(modulationScheme == ModulationType.QAM16):
            return 4
        elif(modulationScheme == ModulationType.QAM64):
            return 6
        else:
            raise InvalidModulationScheme()
            
    def GetSymbol(self,inputData,modulationScheme,transmitPower = 0.5):
        #Creates the complex number acting as the symbol for the input
        numBits = len(inputData)
        if(numBits != self.GetBitsPerSymbol(modulationScheme)):
            raise IncorrectBitsToCreateSymbol()    
    
        if(modulationScheme == ModulationType.BPSK):
            a = np.sqrt(2*transmitPower)
            if inputData == '1':
                symbol = a
            elif inputData == '0':
                symbol = -a
            else:
                raise NonBinaryInput()   
            return symbol
            
        elif(modulationScheme == ModulationType.QPSK):
            a = np.sqrt(2*transmitPower)
            iqDictionary = {
                    '00': [-a,-a],
                    '01': [-a,a],
                    '10': [a,-a],
                    '11': [a,a],
            }
            try:
                i = iqDictionary.get(inputData)[0]
                q = iqDictionary.get(inputData)[1]
                symbol = i + 1j*q
            except(KeyError):
                raise NonBinaryInput()
            return symbol
        
        elif(modulationScheme == ModulationType.QAM16):
            a = np.sqrt(2*transmitPower)
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
            try:
                i = iqDictionary.get(inputData)[0]
                q = iqDictionary.get(inputData)[1]
                symbol = i + 1j*q
            except(KeyError):
                raise NonBinaryInput()
            return symbol
        elif(modulationScheme == ModulationType.QAM64):
            a = np.sqrt(2*transmitPower)
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
            try:
                i = iqDictionary.get(inputData)[0]
                q = iqDictionary.get(inputData)[1]
                symbol = i + 1j*q
            except(KeyError):
                raise NonBinaryInput()
            return symbol
        else:
            raise InvalidModulationScheme()
            
            
    def CreateWaveForSymbol(self,complexSymbol,symbolsAlreadyTransmitted = 0,messageTime = 1/GlobalSettings.messageFrequency):
        bitTransmitTime = np.arange(symbolsAlreadyTransmitted*messageTime,(symbolsAlreadyTransmitted*messageTime) + messageTime,GlobalSettings.sampleTime)
        i = complexSymbol.real
        q = complexSymbol.imag
        output = []
        output.extend(i*np.cos(2*np.pi*self.fc*bitTransmitTime) + q*np.sin(2*np.pi*self.fc*bitTransmitTime))
        return output
    
    def CreateTransmission(self, symbol):
        transmission = Transmission(symbol)
        return transmission
    
    def BinStreamToSymbols(self,binStream,modulationScheme):
        bitsPerSymbol = self.GetBitsPerSymbol(modulationScheme)
        numSymbols = len(binStream)/bitsPerSymbol
        symbols = []
        for x in range(numSymbols):
            binData = binStream[x*bitsPerSymbol:x*bitsPerSymbol + bitsPerSymbol]
            symbol = self.GetSymbol(binData,modulationScheme)
            symbols.append(symbol)
        return symbols
    
   
#Test for Class
from FadingChannel import FadingChannel
transmitter = Transmitter()
fullWave = []
fullFadedWave = []
fChannel = FadingChannel(0.01)
binSequence = '1011'
symbols = transmitter.BinStreamToSymbols(binSequence,ModulationType.QAM16)
for symbol in symbols:
    transmission = transmitter.CreateTransmission(symbol)
    transmission2 = transmitter.CreateTransmission(symbol)
    
    #Old Method, will probably not work with Pilots
    fadedSymbol = fChannel.PropogateInput(symbol)
    transmission.UpdateSymbol(fadedSymbol)
    
    #New Method
    fChannel.ApplyFadingToTransmission(transmission2)
    
    #Plotting the 2 waves. Each wave can have components 
    #added manually using its wave property
    plot.plot(transmission.wave)
    plot.plot(transmission2.wave)
    


