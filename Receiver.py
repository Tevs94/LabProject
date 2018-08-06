import numpy as np
import matplotlib.pyplot as plot
from Transmission import Transmission
from ModulationConstellations import ModulationConstellations
from scipy.signal import butter, lfilter, freqz
from scipy import signal
import GlobalSettings

class Receiver():
       
    def CombineReceivedTransmissions(self, transmission1, transmission2):
        #recievedSymbol ONLY FOR TESTING, MUST ADD SYMBOL DETECTION LOGIC
        #receivedSymbol = transmission1.symbol + transmission2.symbol
        receivedWave = (transmission1.wave) + (transmission2.wave)
        receivedSymbol = self.IQWaveToSymbol(receivedWave)

        return receivedSymbol
       
    def AlamoutiCombine(self, h0, h1, r0, r1):
        #r0 and r1 are recieved SYMBOLS
        s0 = h0.conjugate()*r0 + h1*r1.conjugate()
        s1 = h1.conjugate()*r0 + ((-1*h0)*r1.conjugate())
        return [s0,s1]
    
    def MLDSymbolToBinary(self, symbol, ModulationType,transmitPower):
        mod = ModulationConstellations(transmitPower)
        symbolDictionary = mod.GetConstellationDictionary(ModulationType)
        minDis = np.inf
        binOutput = ''
        #Use the dictionary keys and values to get most likely binary value
        keys = symbolDictionary.keys()
        vals = symbolDictionary.values()
        for n in range(len(vals)):
            distance = np.sqrt(np.square(vals[n][0] - symbol.real) + np.square(vals[n][1] - symbol.imag))
            if distance < minDis:
                minDis = distance
                binOutput = keys[n]
        return binOutput
    
    def SphereDetectionSymbolToBinary(self, symbol, ModulationType):
        mod = ModulationConstellations()
        symbolDictionary = mod.GetConstellationDictionary(ModulationType)

        return '01'
    
    def LPFilterWave(self, wave, cutOff, order = 2):
        #Note there is a bit of distortion at the beginning
        fs = float(1)/GlobalSettings.sampleTime
        nyq = 0.5 * fs
        normal_cutoff = cutOff / nyq
        b, a = butter(order, normal_cutoff, analog=False)
        filteredWave = signal.filtfilt(b, a, wave)
        return filteredWave
        
    def IQWaveToSymbol(self, wave):
        
        messageTime = float(1)/GlobalSettings.messageFrequency
        waveTime = np.arange(0, messageTime, GlobalSettings.sampleTime)
        cosWave = np.cos(2*np.pi*GlobalSettings.carrierFrequency*waveTime)
        sinWave = np.sin(2*np.pi*GlobalSettings.carrierFrequency*waveTime)
        iWave = self.LPFilterWave(cosWave*wave,GlobalSettings.carrierFrequency)
        qWave = self.LPFilterWave(sinWave*wave,GlobalSettings.carrierFrequency)
        #Assume need to determine the Magnitude of the waves generated here, not so easy with the distortion happening
        #Maybe remove first 2000 points then grab min and max from that
        cutOffWaveI = iWave[2000:8000]
        cutOffWaveQ = qWave[2000:8000]
        i = 2*sum(cutOffWaveI)/len(cutOffWaveI)
        q = 2*sum(cutOffWaveQ)/len(cutOffWaveQ)
        return i + 1j*q