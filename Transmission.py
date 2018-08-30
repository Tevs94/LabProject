import GlobalSettings
import numpy as np

class Transmission():
    def __init__(self, symbol,messageFreq = GlobalSettings.messageFrequency, carrierFreq = GlobalSettings.carrierFrequency):
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
        #Warning: Overwrites waveform, don't use with Pilot
        self.symbol = newSymbol
        self.wave = self.CreateWave()
        
    def MultiplySymbol(self, h):
        #Will be used to multiply symbol by h and adjust the waveform
        angleH = np.angle(h)
        print "real ANGLE:", angleH
        magH = abs(h)
        print "Real mag", magH
        self.symbol = (self.symbol*h)
        self.PhaseShiftWave(angleH)
        self.AmplitudeMultiplyWave(magH)
    
    def AddSymbol(self, n):
        #Will be used to add the noise. Changes symbol and adjusts waveform without losing data from waveform
        anglePrev = np.angle(self.symbol)
        magPrev = abs(self.symbol)
        self.symbol = self.symbol + n
        newAngle = np.angle(self.symbol)
        newMag = abs(self.symbol)
        changeAngle = newAngle - anglePrev
        changeMag = newMag / magPrev
        self.PhaseShiftWave(changeAngle)
        self.AmplitudeMultiplyWave(changeMag)

    def PhaseShiftWave(self, angle):
        carrierTime = float(1)/(self.fc)
        carrierLength = (carrierTime)/GlobalSettings.sampleTime
        numShifts = int(round(carrierLength*(angle/(np.pi*2))))
        print "Real shifts", numShifts
        self.wave = np.roll(self.wave,numShifts)
    
    def AmplitudeMultiplyWave(self, amplitude):
        self.wave = self.wave * amplitude
        
    def OverideWave(self, signal):
        self.wave = signal