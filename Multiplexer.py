from OSTBCEnums import MultiplexerType
from OSTBCEnums import ModulationType #for testinmg
import numpy as np
import GlobalSettings
import matplotlib.pyplot as plot
import Transmitter as Transmitter

class Multiplexer():
     
    def __init__(self, muxType, symbol, transmitter = 0, carrierFrequency = GlobalSettings.carrierFrequency ,muxCarrierFrequency = GlobalSettings.multiplexCarrierFrequency, messageFrequency = GlobalSettings.messageFrequency, carrierAmplitude = GlobalSettings.multiplexCarrierAmplitude, sampleTime = GlobalSettings.sampleTime):
        self.fmux = muxCarrierFrequency
        if(transmitter == 1):
            self.fmux = 3*muxCarrierFrequency
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
    #This applys TDM and FDM to a data signal with the generated pilot waveform
    def SerialToParallel(self):
        inputSignal = [[]*2 for _ in range(2)]
        pilotSignal = [[]*2 for _ in range(2)]
        inputSignal[1][:] = self.symbol.wave
        if(self.type == MultiplexerType.FDM): #Perform Coventional AM, currently set up for 2 by 1 with assumption same carrier is fine
            inputSignal[0][:] = self.GeneratePilot()
            for x in range(0, 2): #Nyquist to fc
                pilotSignal[x][:] = self.DSB_SC(inputSignal[x][:], 8*self.fc*x)
            self.ParallelToSerial(pilotSignal)
        if(self.type == MultiplexerType.TDM):
            pilotSignal[0][:] = [0]* 2*len(self.time)
            pilotSignal[0][len(self.time):int(2*len(self.time))]  = self.GeneratePilot(self.transmitter + 1)
            pilotSignal[0][0:len(self.time)] = inputSignal[1][:]
            self.wave = pilotSignal[0]
            
    #For FDM combines modulated signals
    def ParallelToSerial(self, signal):
        self.wave = np.array(signal[0]) +  np.array(signal[1])
#     
    #Creates pilot waveforms
    def GeneratePilot(self, factor = 1):
        outputSignal = np.array(np.cos(2 * np.pi * factor * self.fc * self.time))
        return outputSignal
    
    #No longer used due to normalization issues, kept incase needed
    def DSB_FC(self, signal, shift, factor = 1):
        maxSignal = np.amax(signal)
        normalizedSignal = np.array([(x/maxSignal) for x in signal])
        preCarrier = np.array([(factor * x)+1 for x in normalizedSignal])
        carrier = np.array(np.cos(2 * np.pi * (self.fmux + shift) * self.time))
        postCarrierNoAmp = np.multiply(preCarrier,carrier)
        outputSignal = np.multiply(self.ac,postCarrierNoAmp)
        return outputSignal
    
    #used for FDM, waveform modulation
    def DSB_SC(self, signal, shift):
        carrier = np.array(np.cos(2 * np.pi * (self.fmux + shift) * self.time))
        outputSignal = np.multiply(signal,carrier)
        return outputSignal