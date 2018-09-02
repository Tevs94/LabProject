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
from scipy.signal import firwin, convolve, freqs
from copy import deepcopy
from Transmission import Transmission


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
        self.fakeTransmission = Transmission(1)
        self.cleanPilot, self.cosWave = self.GeneratePilot(False)
        self.s0, self.h0 = self.SignalDetector(signal0)
        self.fmux = 3* muxCarrierFrequency
        if(self.type == MultiplexerType.TDM):
            self.cleanPilot, self.cosWave = self.GeneratePilot(False,2)
        self.s1, self.h1 = self.SignalDetector(signal1)
            
    def BandPassFilter(self, lowerLimit, upperLimit, signal,order = 2):
        nyq = 0.5 * (1/self.ts)
        low = lowerLimit/nyq
        high = upperLimit/nyq
        b, a = butter(order, [low, high], btype='band', analog=False) #b = num a = denom
        y = filtfilt(b,a,signal, method = 'gust')
        return y 
    
    def DemodulateDSB_SC(self, signal, frequency, shift, angle):
        freq = 2 * np.pi * (self.fmux + shift) * self.time 
        demodCarrier = np.array(np.cos(freq -angle))       
        preDemod = np.multiply(signal,demodCarrier)
        lpfSignal = self.LowPassFilter(frequency, preDemod) #LPF
        ampFixSignal = np.array([((x*2)) for x in lpfSignal])
        return ampFixSignal
    
    def DemodulateDSB_FC(self, signal, frequency ,pilot = True):
        signal[signal < 0] = 0 #Rectify
        lpfSignal = self.LowPassFilter(frequency, signal) #LPF
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
        outputSignal = np.array(np.cos(2 * np.pi * factor * self.fc * self.time))
        carrier = np.array(np.cos(2 * np.pi * (self.fmux) * self.time))
        modulatedSignal = np.multiply(outputSignal,carrier)
        y = self.DemodulateDSB_SC(modulatedSignal, 3*self.fc, 0,0)
        return y, outputSignal

    
    def ChannelEstimator(self, pilot, signal):
        maxPilot = float(np.amax(pilot[self.quaterPoint:len(self.time)-self.quaterPoint]))
        maxSignal = float(np.amax(signal[self.quaterPoint:len(self.time)-self.quaterPoint]))
        magnitude = np.divide(maxSignal,maxPilot) #6,02% error here to magH
        factor = np.divide(maxPilot,maxSignal)
        ampFixSignal = np.array([x*factor for x in signal])
        period = float(1.0/self.fc) #in this case for my pilot
        length = period/(self.ts)
        halfPeriod = int(float(length/2.0))
        shift = np.argmax(ampFixSignal[self.halfPoint - 0* halfPeriod:self.halfPoint +2* halfPeriod])
        angle = 2*np.pi* shift*(1/length)
        return magnitude, angle
        
    def SignalDetector(self, signal):
        if(self.type == MultiplexerType.FDM):  
            pilotSignal = self.BandPassFilter(self.fmux - 4*self.fc,self.fmux + 4*self.fc,signal)
            magnitude = self.EstimatePilotMaxWithFFT(pilotSignal)
            pilot1= self.DemodulateDSB_SC(pilotSignal, 3*self.fc,0,0)
            goodMag, badAngle = self.ChannelEstimator(self.cleanPilot ,pilot1)
            pilot2= self.DemodulateDSB_SC(pilotSignal, 3*self.fc,0,badAngle)
            badMag, goodAngle = self.ChannelEstimator(self.cleanPilot ,pilot2) 
            channel = (magnitude * np.cos(goodAngle)) + (1j * magnitude* np.sin(goodAngle))
            
            correct = [False] * 4
            channels = [0] * 4
            channels[0] = (magnitude * np.cos(goodAngle)) + (1j * magnitude* np.sin(goodAngle))
            self.fakeTransmission.OverideWave(self.cosWave)
            self.fakeTransmission.MultiplySymbol(channels[0])
            correct[0] = self.QuadrantSelect(pilot2[4750:5250],self.fakeTransmission.wave[4750:5250])
            
            channels[1] = complex(-1*channels[0].real,-1*channels[0].imag)
            self.fakeTransmission.OverideWave(self.cosWave)
            self.fakeTransmission.MultiplySymbol(channels[1])
            correct[1] = self.QuadrantSelect(pilot2[4750:5250],self.fakeTransmission.wave[4750:5250])
            
            channels[2] = complex(-1*channels[0].real,channels[0].imag)
            self.fakeTransmission.OverideWave(self.cosWave)
            self.fakeTransmission.MultiplySymbol(channels[2])
            correct[2] = self.QuadrantSelect(pilot2[4750:5250],self.fakeTransmission.wave[4750:5250])
            
            channels[3] = complex(channels[0].real,-1*channels[0].imag)
            self.fakeTransmission.OverideWave(self.cosWave)
            self.fakeTransmission.MultiplySymbol(channels[3])
            correct[3] = self.QuadrantSelect(pilot2[4750:5250],self.fakeTransmission.wave[4750:5250])
            n = 0
            for truth in correct:
                if(truth==True):
                    channel = channels[n]
                    break
                n+=1
            
            self.fakeTransmission.OverideWave(self.cosWave)
            self.fakeTransmission.MultiplySymbol(channel)
            maxP = np.argmax(pilot1[:1000])
            maxT = np.argmax(self.fakeTransmission.wave[:1000])
            if(abs(maxP-maxT) < 250 or abs(maxP-maxT) > 500):
                channel = complex(-1*channel.real,-1*channel.imag)
                self.fakeTransmission.OverideWave(self.cosWave)
                self.fakeTransmission.MultiplySymbol(channel)
                
            dataSignal = self.BandPassFilter(self.fmux + 4*self.fc,self.fmux + 12 * self.fc,signal)
            data = self.DemodulateDSB_SC(dataSignal, 3 * self.fc,8*self.fc,goodAngle)
            return data, channel
        if(self.type == MultiplexerType.TDM):
            pilotSignal = signal[len(self.time):int(2*len(self.time))]
            dataSignal = signal[0:len(self.time)]
            magnitude, angle = self.ChannelEstimator(self.cleanPilot ,pilotSignal)
            channel = (magnitude * np.cos(angle)) + (1j * magnitude* np.sin(angle))
            return dataSignal, channel        
            
    def FFT(self, signal):
        n = len(signal) # length of the signal
        k = np.arange(n)
        T = n/(1/self.ts)
        frq = k/T # two sides frequency range
        frq = frq[range(n/40)] # one side frequency range
        Y = np.fft.fft(signal)/n # fft computing and normalization
        Y = Y[range(n/40)]
        fig, ax = plot.subplots(2, 1)
        ax[1].plot(frq,abs(Y),'r') # plotting the spectrum
        ax[1].set_xlabel('Freq (Hz)')
        ax[1].set_ylabel('|Y(freq)|')
        
    def PrintFilter(self,b,a, nyq):
        plot.figure()
        plot.clf()
        w, h = freqs(b, a, worN=2000)
        plot.plot((nyq/np.pi)*w, abs(h))
        #plt.xscale('linear')
        plot.title('Butterworth filter frequency response')
        plot.xlabel('Frequency [Hz]')
        plot.ylabel('Amplitude')
        plot.margins(0, 0.1)
        plot.grid(which='both', axis='both')
        
    def EstimatePilotMaxWithFFT(self, modulatedPilot, pilotMagnitude = 1):       
        fftPilot = np.fft.fft(modulatedPilot)/len(modulatedPilot) # fft computing and normalization
        return (max(abs(fftPilot))*4)/pilotMagnitude
        
    def QuadrantSelect(self, pilot, tansmission):
        maxP = np.amax(pilot)
        maxT = np.amax(tansmission)
        sumP = np.sum(pilot)
        sumT = np.sum(tansmission)
        diffP = sumP-maxP
        diffT = sumT-maxT
        difference = abs(diffP-diffT)
        if(difference < 50):
            return True
        else:
            return False