import random
import numpy as np
import matplotlib.pyplot as plot

class FadingChannel():
    def __init__(self, noiseDeviation = np.sqrt(0.5)):
        random.seed()
        self.h = random.gauss(0, np.sqrt(0.5)) + 1j*random.gauss(0,np.sqrt(0.5))
        self.noise = random.gauss(0, noiseDeviation) + 1j*random.gauss(0, noiseDeviation)
       
    def ApplyFadingToTransmission(self, transmission):
        #transmission is a Transmission object
        # y = hx + n 
        transmission.MultiplySymbol(self.h)
        transmission.AddSymbol(self.noise)   
    
    
