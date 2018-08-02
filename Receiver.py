import numpy as np
import matplotlib.pyplot as plot
from Transmission import Transmission
from ModulationConstellations import ModulationConstellations

class Receiver():
       
    def CombineReceivedTransmissions(self, transmission1, transmission2):
        #recievedSymbol ONLY FOR TESTING, MUST ADD SYMBOL DETECTION LOGIC
        receivedSymbol = transmission1.symbol + transmission2.symbol
        receivedWave = transmission1.wave + transmission2.wave
        return receivedSymbol
       
    def AlamoutiCombine(self, h0, h1, r0, r1):
        #r0 and r1 are recieved SYMBOLS
        s0 = h0.conjugate()*r0 + h1*r1.conjugate()
        s1 = h1.conjugate()*r0 - h0*r1.conjugate()
        return [s0,s1]
    
    def MLDSymbolToBinary(self, symbol, ModulationType):
        mod = ModulationConstellations()
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
        
