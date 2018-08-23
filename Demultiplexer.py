from OSTBCEnums import MultiplexerType
import numpy as np
import GlobalSettings
from scipy.signal import butter, filtfilt

class Demultiplexer():
    def __init__(self, muxType, signal0, signal1, carrierFrequency = GlobalSettings.carrierFrequency ,muxCarrierFrequency = GlobalSettings.multiplexCarrierFrequency, messageFrequency = GlobalSettings.messageFrequency, carrierAmplitude = GlobalSettings.multiplexCarrierAmplitude, sampleTime = GlobalSettings.sampleTime):
        self.fmux = muxCarrierFrequency
        self.fc = carrierFrequency
        self.fm = messageFrequency
        self.ac = carrierAmplitude
        self.ts = sampleTime
        self.type = muxType
        self.time = np.arange(0,1/self.fm,self.ts)
        self.roll = int((1.0/self.fc)/4.0*100000)
        self.quaterPoint = int(len(self.time)/4.0) #used to ensure correct normaliZaTION
        #below we handle transmitters
        self.s0, self.h0 = self.SignalDetector(signal0)
        self.s1, self.h1 = self.SignalDetector(signal1)
            
    def BandPassFilter(self, lowerLimit, upperLimit, signal,order = 2):
        nyq = 0.5 * (1/self.ts)
        low = lowerLimit/nyq
        high = upperLimit/nyq
        b, a = butter(order, [low, high], btype='band', analog=False) #b = num a = denom
        rolled = self.Roller(signal)
        y = filtfilt(b,a,rolled)
        derolled = self.DeRoller(y)
        return derolled
    
    def Roller(self, signal):
        y = np.roll(signal, self.roll)
        return y
    
    def DeRoller(self, signal):
        y = np.roll(signal, -1* self.roll)
        return y
    
    def DemodulateDSB_FC(self, signal, frequency ,pilot = True):
        signal[signal < 0] = 0 #Rectify
        lpfSignal = self.LowPassFilter(frequency, signal) #LPF
        #Fine tunning to remove filter error
        if(pilot == True):
            lpfSignal = np.array([((x * 0.705405261084362) + 0.09967367179518072) for x in lpfSignal]) #Corrects clean pilot to 0.9999999999999984 bandpass fikltered pilot
        if(pilot == False):
            lpfSignal = np.roll(lpfSignal, -int(self.roll * 0.35))
        dc = np.mean(lpfSignal)
        noDCSignal = np.array([x-dc for x in lpfSignal])
        demodulatedSignalMax = np.amax(noDCSignal[self.quaterPoint:len(self.time)-self.quaterPoint])
        correctedSignal = np.array([x*(1/demodulatedSignalMax) for x in noDCSignal])
        return correctedSignal, lpfSignal
        
    def LowPassFilter(self, frequency, signal,order = 4):
        nyq = 0.3 * (1/self.ts)
        Wc = frequency/nyq
        b, a = butter(order, Wc, btype='low') #b = num a = denom
        y = filtfilt(b, a, signal)
        trimVal = int(4.0*self.roll)
        trimTop = y[0:y.size-trimVal]
        trimBot = trimTop[trimVal:trimTop.size]
        return trimBot
    
    def GeneratePilot(self, factor = 1):
        pilot = np.cos(2 * np.pi * self.fc * self.time)
        preCarrier = np.array([(factor * x)+1 for x in pilot])
        carrier = np.array(np.cos(2 * np.pi * (self.fmux) * self.time))
        postCarrierNoAmp = np.multiply(preCarrier,carrier)
        modulatedSignal = np.multiply(self.ac,postCarrierNoAmp)
        #DSB_FC done now demodulating for expect pilot
        y, z = self.DemodulateDSB_FC(modulatedSignal, self.fc)
        return y, z
    
    def ChannelEstimator(self, pilot, signal):
        maxPilot = np.amax(pilot)
        maxSignal = float(np.amax(signal))
        difference = np.divide(maxPilot,maxSignal)
        ampFixSignal = np.array([x*difference for x in signal])
        crossCorrelated = np.correlate(ampFixSignal, pilot)
        peak = np.argmax(crossCorrelated)
        period = float(1.0/self.fc) #in this case for my pilot
        length = period/(self.ts)
        shift = peak/length
        angle = int(shift * (2*np.pi))
        self.channel = (difference * np.cos(angle)) + (1j * difference * np.sin(angle))
        return self.channel
        
    def SignalDetector(self, signal):
        if(self.type == MultiplexerType.FDM):    
            pilotSignal = self.BandPassFilter(self.fmux - self.fc,self.fmux + self.fc,signal)
            pilot, preAdjustmentP = self.DemodulateDSB_FC(pilotSignal, self.fc, False)
            cleanPilot, preAdjustmentCP = self.GeneratePilot()
            channel = self.ChannelEstimator(preAdjustmentCP ,preAdjustmentP)
            dataSignal = self.BandPassFilter(self.fmux + self.fc,self.fmux + 3 * self.fc,signal)
            data, preAdjustmentD = self.DemodulateDSB_FC(dataSignal, 2 * self.fc, False)
            return data, channel
        else:
            a = self.BandPassFilter(self.fmux - self.fc,self.fmux + self.fc,signal)
            self.DemodulateDSB_FC(a)