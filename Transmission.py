import GlobalSettings
import numpy as np

class Transmission():
    def __init__(self, symbol, messageFreq = GlobalSettings.messageFrequency, carrierFreq = GlobalSettings.carrierFrequency):
        self.fc = carrierFreq
        self.mf = messageFreq
        self.symbol = symbol
        self.wave = self.CreateWave()
    
    def CreateWave(self):
        messageTime = 1/self.mf
        bitTransmitTime = np.arange(0, messageTime,GlobalSettings.sampleTime)
        i = self.symbol.real
        q = self.symbol.imag
        output = []
        output.extend(i*np.cos(2*np.pi*self.fc*bitTransmitTime) + q*np.sin(2*np.pi*self.fc*bitTransmitTime))
        return output
        
    def UpdateSymbol(self, newSymbol):
        self.symbol = newSymbol
        self.wave = self.CreateWave()
        
    def MultiplySymbol(self, h):
        #Will be used to multiply symbol by h and adjust the waveform
        angleH = np.angle(h)
        magH = abs(h)
        self.symbol = (self.symbol*h)
        self.PhaseShiftWave(angleH)
        self.AmplitudeShiftWave(magH)
    
    def AddSymbol(self, otherSymbol):
        #Will be used to add the noise
        #Not yet implemented
        return 0
            
    def PhaseShiftWave(self, angle):
        carrierTime = float(1)/(self.fc)
        carrierLength = (carrierTime)/GlobalSettings.sampleTime
        numShifts = int(round(carrierLength*(angle/(np.pi*2))))
        self.wave = np.roll(self.wave,numShifts)
    
    def AmplitudeShiftWave(self, amplitude):
        self.wave = self.wave * amplitude