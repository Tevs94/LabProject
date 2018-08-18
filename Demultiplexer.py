from OSTBCEnums import MultiplexerType
from OSTBCEnums import ModulationType #for testinmg
import numpy as np
import GlobalSettings
import matplotlib.pyplot as plot
from scipy.signal import butter, lfilter, freqz, firwin, filtfilt, lfilter_zi
import Transmitter as Transmitter
import Multiplexer as Multiplexer

class Demultiplexer():
    def __init__(self, muxType, signal, carrierFrequency = GlobalSettings.carrierFrequency ,muxCarrierFrequency = GlobalSettings.multiplexCarrierFrequency, messageFrequency = GlobalSettings.messageFrequency, carrierAmplitude = GlobalSettings.multiplexCarrierAmplitude, sampleTime = GlobalSettings.sampleTime):
        self.fmux = muxCarrierFrequency
        self.fc = carrierFrequency
        self.fm = messageFrequency
        self.ac = carrierAmplitude
        self.ts = sampleTime
        self.type = muxType
        self.time = np.arange(0,1/self.fm,self.ts)
        self.roll = int((1.0/self.fc)/4.0*100000)
        #below we handle transmitters
        self.SignalDetector(signal)
            
    def BandPassFilter(self, lowerLimit, upperLimit, signal,order = 2):
        nyq = 0.5 * (1/self.ts)
        low = lowerLimit/nyq
        high = upperLimit/nyq
        b, a = butter(order, [low, high], btype='band', analog=False) #b = num a = denom
        rolled = self.Roller(signal)
        y = filtfilt(b,a,rolled)
        derolled = self.DeRoller(y)
        return derolled
        
    def DemodulateDSB_FC(self, signal):
        signal[signal < 0] = 0 #Rectify
        lpfSignal = self.LowPassFilter(self.fc, signal) #LPF
        dc = np.mean(lpfSignal)
        noDCSignal = np.array([x-dc for x in lpfSignal])
        demodulatedSignalMax = np.amax(noDCSignal)
        correctedSignal = np.array([x*(1/demodulatedSignalMax) for x in noDCSignal])
        return correctedSignal
        #plot.plot(correctedSignal)
        
    def LowPassFilter(self, frequency, signal,order = 4):
        nyq = 0.3 * (1/self.ts)
        Wc = frequency/nyq
        b, a = butter(order, Wc, btype='low') #b = num a = denom
        y = filtfilt(b, a, signal)
        return y
    
    def GeneratePilot(self, factor = 1):
        pilot = np.cos(2 * np.pi * self.fc * self.time)
        preCarrier = np.array([(factor * x)+1 for x in pilot])
        carrier = np.array(np.cos(2 * np.pi * (self.fmux) * self.time))
        postCarrierNoAmp = np.multiply(preCarrier,carrier)
        modulatedSignal = np.multiply(self.ac,postCarrierNoAmp)
        rolled = self.Roller(modulatedSignal)
        #DSB_FC done now demodulating for expect pilot
        y =self.DemodulateDSB_FC(rolled)
        deRolled = self.DeRoller(y)
        return deRolled
    
    def Roller(self, signal):
        y = np.roll(signal, self.roll)
        return y
    
    def DeRoller(self, signal):
        y = np.roll(signal, -1* self.roll)
        return y
    
    def ChannelEstimator(self, pilot, signal):
        maxPilot = np.amax(pilot)
        maxSignal = float(np.amax(signal))
        difference = np.divide(maxPilot,maxSignal)
        ampFixSignal = np.array([x/difference for x in signal])
        crossCorrelated = np.correlate(pilot, ampFixSignal, mode='full')
        peak = 10000 - np.argmax(crossCorrelated)
        period = float(1.0/self.fc) #in this case for my pilot
        length = period/(self.ts)
        shift = peak/length
        angle = int(shift * (2*np.pi))
        self.channel = (difference * np.cos(angle)) + (1j * difference * np.sin(angle))
        print self.channel
        
    def SignalDetector(self, signal):
        plot.figure(0)
        plot.clf()
        plot.plot(signal)
        if(self.type == MultiplexerType.FDM):    
            rollFixedSignal = self.BandPassFilter(self.fmux - self.fc,self.fmux + self.fc,signal)
            plot.plot(rollFixedSignal)
            pilot = self.DemodulateDSB_FC(rollFixedSignal)
            plot.figure(1)
            plot.clf()
            plot.plot(pilot, color="#000000")
            cleanPilot = self.GeneratePilot()
            plot.plot(cleanPilot)
            self.ChannelEstimator(cleanPilot ,pilot)
        else:
            a = self.BandPassFilter(self.fmux - self.fc,self.fmux + self.fc,signal)
            #a = self.FIR(124, self.fmux - self.fc,self.fmux + self.fc, 1/self.ts, self.transmittedSignal)
            self.DemodulateDSB_FC(a)
    
        
#Test for Class
from FadingChannel import FadingChannel
transmitter = Transmitter.Transmitter()
fullWave = []
fullFadedWave = []
fChannel = FadingChannel(0.01)
binSequence = '1011'
symbols = transmitter.BinStreamToSymbols(binSequence,ModulationType.QPSK)
transmission = transmitter.CreateTransmission(symbols[0])
Mux = Multiplexer.Multiplexer(MultiplexerType.FDM,transmission)
Demux = Demultiplexer(MultiplexerType.FDM,Mux.wave) 