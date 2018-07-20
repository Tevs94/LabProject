import random
import cmath
import numpy as np
import matplotlib.pyplot as plot

class FadingChannel():
    def __init__(self, noiseDeviation = np.sqrt(0.5)):
        random.seed()
        self.h = random.gauss(0, np.sqrt(0.5)) + 1j*random.gauss(0,np.sqrt(0.5))
        self.noiseDeviation = noiseDeviation
        
    def PropogateInput(self, inputToChannel):
        noiseSize = len(inputToChannel)
        noise = np.random.normal(0, self.noiseDeviation, noiseSize) + 1j*np.random.normal(0, self.noiseDeviation, noiseSize)
        output = (inputToChannel*self.h)+ noise
        return output
    
    def GetH(self):
        return self.h
    
    def GetNoiseDeviation(self):
        return self.noiseDeviation
    
time = np.arange(0,20,0.01)
coswave = np.cos(time)
fd = FadingChannel(0.01)
output = fd.PropogateInput(coswave)
plot.plot(output.real)