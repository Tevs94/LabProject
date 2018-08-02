from OSTBCEnums import ModulationType
import numpy as np
import GlobalSettings
import matplotlib.pyplot as plot
from Transmission import Transmission
from ModulationConstellations import ModulationConstellations 

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
            mod = ModulationConstellations(a)
            iqDictionary = mod.GetConstellationDictionary(modulationScheme)
            try:
                i = iqDictionary.get(inputData)[0]
                q = iqDictionary.get(inputData)[1]
                symbol = i + 1j*q
            except(KeyError):
                raise NonBinaryInput()
            return symbol
        
        elif(modulationScheme == ModulationType.QAM16):
            a = np.sqrt(2*transmitPower)
            mod = ModulationConstellations(a)
            iqDictionary = mod.GetConstellationDictionary(modulationScheme)
            try:
                i = iqDictionary.get(inputData)[0]
                q = iqDictionary.get(inputData)[1]
                symbol = i + 1j*q
            except(KeyError):
                raise NonBinaryInput()
            return symbol
        elif(modulationScheme == ModulationType.QAM64):
            a = np.sqrt(2*transmitPower)
            mod = ModulationConstellations(a)
            iqDictionary = mod.GetConstellationDictionary(modulationScheme)
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
    




