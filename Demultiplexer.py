from OSTBCEnums import MultiplexerType
import numpy as np
import GlobalSettings
from scipy.signal import butter, filtfilt
from AlamoutiScheme import AlamoutiScheme
from FadingChannel import FadingChannel
from Receiver import Receiver
from OSTBCEnums import ModulationType, MultiplexerType, DecoderType
import Multiplexer as Multiplexer
import matplotlib.pyplot as plot

class Demultiplexer():
    def __init__(self, muxType, signal0, signal1 , carrierFrequency = GlobalSettings.carrierFrequency ,muxCarrierFrequency = GlobalSettings.multiplexCarrierFrequency, messageFrequency = GlobalSettings.messageFrequency, carrierAmplitude = GlobalSettings.multiplexCarrierAmplitude, sampleTime = GlobalSettings.sampleTime):
        self.fmux = muxCarrierFrequency
        self.fc = carrierFrequency
        self.fm = messageFrequency
        self.ac = carrierAmplitude
        self.ts = sampleTime
        self.type = muxType
        self.time = np.arange(0,1/self.fm,self.ts)
        self.roll = int((1.0/self.fc)/4.0*(1.0/self.ts))
        self.quaterPoint = int(len(self.time)/4.0) #used to ensure correct normaliZaTION
        self.halfPoint = int(len(self.time)/2.0)
        #below we handle transmitters
        self.cleanPilot, self.preAdjustmentCP = self.GeneratePilot()
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
        #if(pilot == False):
            #lpfSignal = np.roll(lpfSignal, -int(self.roll * 0.35))
        dc = np.mean(lpfSignal[self.quaterPoint:len(self.time)-self.quaterPoint])
        noDCSignal = np.array([x-dc for x in lpfSignal])
        tmpSignal = noDCSignal[self.quaterPoint:len(self.time)-self.quaterPoint]
        tmpSignal[tmpSignal < 0]
        negValuesSignal = -1*tmpSignal
        maxPos = float(np.amax(noDCSignal))
        maxNeg = float(np.amax(negValuesSignal))
        factor = maxPos/maxNeg
        for (i, item) in enumerate(noDCSignal):
            if(item < 0):
                noDCSignal[i] = noDCSignal[i]*factor*0.975
        #offset remains of e-17 to e-18
        demodulatedSignalMax = np.amax(noDCSignal[self.quaterPoint:len(self.time)-self.quaterPoint])
        correctedSignal = np.array([x*(1/demodulatedSignalMax) for x in noDCSignal])
        return correctedSignal, noDCSignal
        
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
        plot.plot(pilot)
        plot.plot(signal,color='red')
        maxPilot = float(np.amax(pilot[self.quaterPoint:len(self.time)-self.quaterPoint]))
        maxSignal = float(np.amax(signal[self.quaterPoint:len(self.time)-self.quaterPoint]))
        print "maxP: ", maxPilot, "maxS: ", maxSignal
        difference = np.divide(maxSignal,maxPilot) #6,02% error here to magH
        difference = difference*0.94
        print "difference", difference
        factor = np.divide(maxPilot,maxSignal)
        ampFixSignal = np.array([x*factor for x in signal])
        period = float(1.0/self.fc) #in this case for my pilot
        length = period/(self.ts)
        halfPeriod = int(float(length/2.0))
        shift = np.argmax(ampFixSignal[self.halfPoint - halfPeriod:self.halfPoint + halfPeriod])
        angle = 2*np.pi* shift*(1/length)
        self.channel = (difference * np.cos(angle)) + (1j * difference * np.sin(angle))
        return self.channel
        
    def SignalDetector(self, signal):
        if(self.type == MultiplexerType.FDM):    
            pilotSignal = self.BandPassFilter(self.fmux - self.fc,self.fmux + self.fc,signal)
            pilot, preAdjustmentP = self.DemodulateDSB_FC(pilotSignal, self.fc, False)
            channel = self.ChannelEstimator(self.preAdjustmentCP ,preAdjustmentP)
            dataSignal = self.BandPassFilter(self.fmux + self.fc,self.fmux + 3 * self.fc,signal)
            data, preAdjustmentD = self.DemodulateDSB_FC(dataSignal, 2 * self.fc, False)
            return data, channel
        else:
            a = self.BandPassFilter(self.fmux - self.fc,self.fmux + self.fc,signal)
            self.DemodulateDSB_FC(a)
            
#Test Code
#binInput = '000000'
#rec = Receiver()
#al = AlamoutiScheme()
#transmissions = al.CreateTransmissions(binInput,ModulationType.BPSK)
#n = 1
#for trans in transmissions[0]:
#    ch0 = FadingChannel(0)
#    h0c = ch0.h
#    Mux10 = Multiplexer.Multiplexer(MultiplexerType.FDM,trans)
#    trans.OverideWave(Mux10.wave)
#    ch0.ApplyFadingToTransmission(trans)
#    Demux1 = Demultiplexer(MultiplexerType.FDM,trans.wave, trans.wave)
#    trans.OverideWave(Demux1.s0)
#    h0d = Demux1.h0
#    print "Real h0: ", h0c, "Estimated h0: ", h0d
#    print ''
#    plot.figure(n)
#    plot.clf()
#    n+=1


#plot.plot(faded.wave, color='green')
#plot.plot(Demux1.s0)
#faded.MultiplySymbol(h0c)
#plot.plot(faded.wave, color='black')