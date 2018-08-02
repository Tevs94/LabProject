from Transmitter import Transmitter
from FadingChannel import FadingChannel
from OSTBCEnums import ModulationType
import matplotlib.pyplot as plot
import numpy as np

class AlamoutiScheme():
        #2 Transmitter objects technically unneccessary since they are not modulating/transmitting in parallel
        #But helps for visualization and readability
       
    def CreateTransmissions(self,binInput,modulationScheme):
        transmitter1 = Transmitter()
        transmitter2 = Transmitter()
        symbols = transmitter1.BinStreamToSymbols(binInput,modulationScheme)
        #2d array of transmissions. 
        #transmissions [transmitter Number][transmission Number] 
        transmissions = [[0 for x in range(len(symbols))] for y in range(2)]
        
        for x in range(len(symbols)/2):
            s0 = symbols[2*x]
            s1 = symbols[2*x + 1]
            s1ConjNeg = -s1.conjugate()
            s0Conj = s0.conjugate()
            
            #Transmitter 1
            transmissions[0][(2*x)] = transmitter1.CreateTransmission(s0)
            transmissions[0][(2*x)+1] = transmitter1.CreateTransmission(s1ConjNeg)

            
            #Transmitter 2
            transmissions[1][(2*x)] = transmitter2.CreateTransmission(s1)
            transmissions[1][(2*x)+1] = transmitter2.CreateTransmission(s0Conj)

        return transmissions