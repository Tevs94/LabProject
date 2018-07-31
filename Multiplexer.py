from OSTBCEnums import MultiplexerType
from OSTBCEnums import ModulationType #for testinmg
import numpy as np
import GlobalSettings
import matplotlib.pyplot as plot
import Transmitter as Transmitter

class Multiplexer():
     
    def __init__(self, muxType, symbol1, symbol2, carrierFrequency = GlobalSettings.carrierFrequency ,muxCarrierFrequency = GlobalSettings.multiplexCarrierFrequency, messageFrequency = GlobalSettings.messageFrequency, carrierAmplitude = GlobalSettings.multiplexCarrierAmplitude, sampleTime = GlobalSettings.sampleTime):
        self.fmux = muxCarrierFrequency
        self.fc = carrierFrequency
        self.fm = messageFrequency
        self.ac = carrierAmplitude
        self.ts = sampleTime
        self.type = muxType
        self.symbol1 = symbol1.wave #Temp till we have signals proceeding then will just set it up to split them here
        self.symbol2 = symbol2.wave
        self.time = np.arange(0,1/self.fm,self.ts)
    
    #Apply mod scheme and pilot
    def SerialToParallel(self):
        inputSignal = [[]*3 for _ in range(3)]
        pilotSignal = [[]*3 for _ in range(3)]
        ifftSignal = [[]*3 for _ in range(3)]
        cyclicSignal = [[]*3 for _ in range(3)]
        outputSignal = np.array([[]*1 for _ in range(10000)])
        inputSignal[0][:] = self.GeneratePilot()
        inputSignal[1][:] = self.symbol1
        inputSignal[2][:] = self.symbol2
        if(self.type == MultiplexerType.FDM): #Perform Coventional AM, currently set up for 2 by 1 with assumption same carrier is fine
            for x in range(0, 3): #Nyquist to fc
                pilotSignal[x][:] = self.DSB_SC(inputSignal[x][:], 2*self.fc*x)
            outputSignal = np.array(pilotSignal[0]) +  np.array(pilotSignal[1]) + np.array(pilotSignal[2])
        if(self.type == MultiplexerType.OFDM):
            for x in range(0, 3):
               pilotSignal[x][:] = self.rect_Modulation(inputSignal[x][:], self.fc*x)
               ifftSignal[x][:] = self.IFFT(pilotSignal[x][:])
               cyclicSignal[x][:] = self.CyclicPrefix(ifftSignal[x][:])
            outputSignal = np.array(cyclicSignal[0]) +  np.array(cyclicSignal[1]) + np.array(cyclicSignal[2])
        return outputSignal
         
    def GeneratePilot(self):
        outputSignal = np.cos(2 * np.pi * self.fc * self.time)
        return outputSignal
    
    def DSB_SC(self, signal, shift, factor = 1):
        preCarrier = np.array([(factor * x)+1 for x in signal])
        carrier = np.array(np.cos(2 * np.pi * (self.fmux + shift) * self.time))
        postCarrierNoAmp = np.multiply(preCarrier,carrier)
        outputSignal = np.multiply(self.ac,postCarrierNoAmp)
        return outputSignal
    
    def rect_Modulation(self, signal, shift):
        rect = np.zeros(int((1/self.fm)/self.ts))
        middleIndex = int(float(len(rect)/2) + (0.5 if float(len(rect)) % 2 != 0 else 0))
        width = int(np.divide(np.divide(np.divide(1.0, self.fc),2.0),self.ts))
        rect[middleIndex-width:middleIndex+width] = self.ac #though mathetically this creates a sinc(f) with correct bw not sure yet
        #rect[:] = self.ac
        modulatedSignal = (rect * np.exp(-1j * shift * self.time)) * signal
        return modulatedSignal
    
    def IFFT(self, signal):
        output = np.fft.ifft(signal)
        return output
    
    def CyclicPrefix(self, signal):
         middle = int(float(len(signal)/2) + (0.5 if float(len(signal)) % 2 != 0 else 0))
         tail = int(float(middle/2) + (0.5 if float(middle/2) % 2 != 0 else 0))
         outputSignal = np.append(signal,signal[0:tail])
         return outputSignal
            
        
#Test for Class
from FadingChannel import FadingChannel
transmitter = Transmitter.Transmitter()
fullWave = []
fullFadedWave = []
fChannel = FadingChannel(0.01)
binSequence = '1011'
symbols = transmitter.BinStreamToSymbols(binSequence,ModulationType.QPSK)
transmission = transmitter.CreateTransmission(symbols[0])
transmission2 = transmitter.CreateTransmission(symbols[1])
Mux = Multiplexer(MultiplexerType.FDM,transmission, transmission2)      
n = Mux.SerialToParallel()

plot.plot(n)