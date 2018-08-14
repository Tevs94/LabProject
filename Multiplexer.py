from OSTBCEnums import MultiplexerType
from OSTBCEnums import ModulationType #for testinmg
import numpy as np
import GlobalSettings
import matplotlib.pyplot as plot
import Transmitter as Transmitter

class Multiplexer():
     
    def __init__(self, muxType, symbol, transmitter = 0, carrierFrequency = GlobalSettings.carrierFrequency ,muxCarrierFrequency = GlobalSettings.multiplexCarrierFrequency, messageFrequency = GlobalSettings.messageFrequency, carrierAmplitude = GlobalSettings.multiplexCarrierAmplitude, sampleTime = GlobalSettings.sampleTime):
        self.fmux = muxCarrierFrequency * (transmitter + 1)
        self.fc = carrierFrequency
        self.fm = messageFrequency
        self.ac = carrierAmplitude
        self.ts = sampleTime
        self.type = muxType
        self.symbol = symbol #Temp till we have signals proceeding then will just set it up to split them here
        self.time = np.arange(0,1/self.fm,self.ts)
        self.transmitter = transmitter
        self.SerialToParallel()
    
    #Apply mod scheme and pilot
    def SerialToParallel(self):
        inputSignal = [[]*2 for _ in range(2)]
        pilotSignal = [[]*2 for _ in range(2)]
        ifftSignal = [[]*2 for _ in range(2)]
        cyclicSignal = [[]*2 for _ in range(2)]
        inputSignal[0][:] = self.GeneratePilot()
        inputSignal[1][:] = self.symbol.wave
        if(self.type == MultiplexerType.FDM): #Perform Coventional AM, currently set up for 2 by 1 with assumption same carrier is fine
            for x in range(0, 2): #Nyquist to fc
                pilotSignal[x][:] = self.DSB_FC(inputSignal[x][:], 2*self.fc*x)
            self.ParallelToSerial(pilotSignal)
        if(self.type == MultiplexerType.OFDM):
            for x in range(0, 2):
               pilotSignal[x][:] = self.rect_Modulation(inputSignal[x][:], self.fc*x)
               ifftSignal[x][:] = self.IFFT(pilotSignal[x][:])
               cyclicSignal[x][:] = self.CyclicPrefix(ifftSignal[x][:])
            self.ParallelToSerial(cyclicSignal)
    
    def ParallelToSerial(self, signal):
        tmp = np.array(signal[0]) +  np.array(signal[1])
        self.wave = np.roll(tmp,500)
            
#    def ParallelToSerial(self, signal):
#        self.wave = np.array(signal[0]) +  np.array(signal[1])
#        
    def GeneratePilot(self):
        outputSignal = np.cos(2 * np.pi * self.fc * self.time)
        return outputSignal
    
    def DSB_FC(self, signal, shift, factor = 1):
        maxSignal = np.amax(signal)
        normalizedSignal = np.array([(x/maxSignal) for x in signal])
        preCarrier = np.array([(factor * x)+1 for x in normalizedSignal])
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