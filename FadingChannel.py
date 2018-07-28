import random
import cmath
import numpy as np
import matplotlib.pyplot as plot
from Transmission import Transmission

class FadingChannel():
    def __init__(self, noiseDeviation = np.sqrt(0.5)):
        random.seed()
        self.h = random.gauss(0, np.sqrt(0.5)) + 1j*random.gauss(0,np.sqrt(0.5))
        self.noiseDeviation = noiseDeviation
        #Change this when noise is better understood
        self.noise = 0
        
    def PropogateInput(self, inputToChannel):
        #Possibly will be deprecated
        #noiseSize = len(inputToChannel)
        #noise = np.random.normal(0, self.noiseDeviation, noiseSize) + 1j*np.random.normal(0, self.noiseDeviation, noiseSize)
        #noise = random.gauss(0, np.sqrt(0.5)) + 1j*random.gauss(0,np.sqrt(0.5))
        noise = 0
        output = (inputToChannel*self.h)+ noise
        return output
    
    def ApplyFadingToTransmission(self, transmission):
        #transmission is a Transmission object
        # y = hx + n 
        transmission.MultiplySymbol(self.h)
        transmission.AddSymbol(self.noise)   
    
