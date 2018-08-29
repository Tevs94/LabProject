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
from scipy.signal import firwin, convolve

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
#        self.cleanPilot, self.preAdjustmentCP = self.GeneratePilot()
        self.cleanPilot = self.GeneratePilot(False)
        self.s0, self.h0 = self.SignalDetector(signal0)
        self.s1, self.h1 = self.SignalDetector(signal1)
            
    def BandPassFilter(self, lowerLimit, upperLimit, signal,order = 2):
        nyq = 0.5 * (1/self.ts)
        low = lowerLimit/nyq
        high = upperLimit/nyq
        b, a = butter(order, [low, high], btype='band', analog=False) #b = num a = denom
        #rolled = self.Roller(signal)
        y = filtfilt(b,a,signal, method = 'gust')
        #derolled = self.DeRoller(y)
#        nyq = 0.5 * (1/self.ts)
#        bandpass = firwin(128, [lowerLimit, upperLimit], nyq=nyq, pass_zero=False, window='hamming', scale=False)
#        filtered = convolve(signal, bandpass, mode='same')
        return y 
    
    def Roller(self, signal):
        y = np.roll(signal, self.roll)
        return y
    
    def DeRoller(self, signal):
        y = np.roll(signal, -1* self.roll)
        return y
    
    def DemodulateDSB_SC(self, signal, frequency, shift):
        demodCarrier = np.array(np.cos(2 * np.pi * (self.fmux + shift) * self.time))
        preDemod = np.multiply(signal,demodCarrier)
        lpfSignal = self.LowPassFilter(frequency, preDemod) #LPF
        ampFixSignal = np.array([x*4 for x in lpfSignal])
        return ampFixSignal
    
    def DemodulateDSB_FC(self, signal, frequency ,pilot = True):
     
        signal[signal < 0] = 0 #Rectify
        lpfSignal = self.LowPassFilter(frequency, signal) #LPF
        #Fine tunning to remove filter error
        #if(pilot == True):
        #    lpfSignal = np.array([((x * 0.705405261084362) + 0.09967367179518072) for x in lpfSignal]) #Corrects clean pilot to 0.9999999999999984 bandpass fikltered pilot
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
                noDCSignal[i] = noDCSignal[i]*factor
#        #offset remains of e-17 to e-18
   
        demodulatedSignalMax = np.amax(noDCSignal[self.quaterPoint:len(self.time)-self.quaterPoint])
        correctedSignal = np.array([x*(1/demodulatedSignalMax) for x in noDCSignal])
        return correctedSignal, noDCSignal
        
    def LowPassFilter(self, frequency, signal,order = 4):
        nyq = 0.5 * (1/self.ts)
        Wc = frequency/nyq
        b, a = butter(order, Wc, btype='low') #b = num a = denom
        y = filtfilt(b, a, signal,method = 'gust')
        trimVal = int(4.0*self.roll)
        trimTop = y[0:y.size-trimVal]
        trimBot = trimTop[trimVal:trimTop.size]
        return trimBot
    
    def GeneratePilot(self, DSB_FC= True, factor = 1):
        pilot = np.cos(2 * np.pi * self.fc * self.time)
        if(DSB_FC == True):
            preCarrier = np.array([(factor * x)+1 for x in pilot])
            carrier = np.array(np.cos(2 * np.pi * (self.fmux) * self.time))
            postCarrierNoAmp = np.multiply(preCarrier,carrier)
            modulatedSignal = np.multiply(self.ac,postCarrierNoAmp)
            #DSB_FC done now demodulating for expect pilot
            y, z = self.DemodulateDSB_FC(modulatedSignal, self.fc, 0)
            return y, z
        else:
            carrier = np.array(np.cos(2 * np.pi * (self.fmux) * self.time))
            modulatedSignal = np.multiply(pilot,carrier)
            y = self.DemodulateDSB_SC(modulatedSignal, self.fc, 0)
            return y

    
    def ChannelEstimator(self, pilot, signal):
        maxPilot = float(np.amax(pilot[self.quaterPoint:len(self.time)-self.quaterPoint]))
        maxSignal = float(np.amax(signal[self.quaterPoint:len(self.time)-self.quaterPoint]))
        print "maxP: ", maxPilot, "maxS: ", maxSignal
        difference = np.divide(maxSignal,maxPilot) #6,02% error here to magH
        difference = difference
        print "difference", difference
        factor = np.divide(maxPilot,maxSignal)
        ampFixSignal = np.array([x*factor for x in signal])
        period = float(1.0/self.fc) #in this case for my pilot
        length = period/(self.ts)
        halfPeriod = int(float(length/2.0))
        shift = np.argmax(ampFixSignal[self.halfPoint:self.halfPoint + 2*halfPeriod])
        angle = 2*np.pi* shift*(1/length)
        self.channel = (difference * np.cos(angle)) + (1j * difference * np.sin(angle))
        return self.channel
        
    def SignalDetector(self, signal):
        if(self.type == MultiplexerType.FDM):    
            pilotSignal = self.BandPassFilter(self.fmux - 1.2*self.fc,self.fmux + 1.2*self.fc,signal)
#            pilot, preAdjustmentP = self.DemodulateDSB_SC(pilotSignal, self.fc,0)
            pilot= self.DemodulateDSB_SC(pilotSignal, self.fc,0)
            channel = self.ChannelEstimator(self.cleanPilot ,pilot)
            dataSignal = self.BandPassFilter(self.fmux + self.fc,self.fmux + 3 * self.fc,signal)
#            data, preAdjustmentD = self.DemodulateDSB_SC(dataSignal, 2 * self.fc,1)
            data = self.DemodulateDSB_SC(dataSignal, 2 * self.fc,2*self.fc)
            return data, channel
        else:
            a = self.BandPassFilter(self.fmux - self.fc,self.fmux + self.fc,signal,1)
            self.DemodulateDSB_FC(a)
            
#Test Code
binInput = '11'
rec = Receiver()
al = AlamoutiScheme()
transmissions = al.CreateTransmissions(binInput,ModulationType.BPSK)
n = 1
plot.figure(12)
plot.clf()
mux0 = Multiplexer.Multiplexer(MultiplexerType.FDM,transmissions[0][0])
mux1 = Multiplexer.Multiplexer(MultiplexerType.FDM,transmissions[0][1])
plot.plot(transmissions[0][0].wave, color='purple')
plot.plot(transmissions[0][1].wave, color="green")
plot.figure(13)
plot.clf()
plot.plot(mux0.wave, color='purple')
plot.plot(mux1.wave, color="green")

for trans in transmissions[0]:
#    plot.figure(n)
#    plot.clf()
    ch0 = FadingChannel(0)
    ch0.h = 1
    h0c = ch0.h
    
    Mux10 = Multiplexer.Multiplexer(MultiplexerType.FDM,trans)
    trans.OverideWave(Mux10.wave)
    ch0.ApplyFadingToTransmission(trans)
    Demux1 = Demultiplexer(MultiplexerType.FDM,trans.wave, trans.wave)
    trans.OverideWave(Demux1.s0)
    plot.figure()
    plot.clf()
    plot.plot(trans.wave)
    h0d = Demux1.h0
    print "Real h0: ", h0c, "Estimated h0: ", h0d
    print ''
    n+=1


#plot.plot(faded.wave, color='green')
#plot.plot(Demux1.s0)
#faded.MultiplySymbol(h0c)
#plot.plot(faded.wave, color='black')