import random

class FadingChannel():
    def __init__(self, minH, maxH, noiseDeviation):
        random.seed()
        self.h = random.uniform(minH,maxH)
        self.noise = random.gauss(0,noiseDeviation)
        
    def PropogateInput(self, inputToChannel):
        output = (inputToChannel*self.h)+ self.noise
        return output
    
    def GetH(self):
        return self.h
    
    def GetNoise(self):
        return self.noise
    
