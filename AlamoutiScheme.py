from Transmitter import Transmitter

class AlamoutiScheme():
        #2 Transmitter objects technically unneccessary since they are not modulating/transmitting in parallel
        #But helps for visualization and readability
       
    def AlamoutiTransmission(self,binInput,modulationScheme):
        transmitter1 = Transmitter()
        transmitter2 = Transmitter()
        symbols = self.transmitter1.BinStreamToSymbols(binInput,modulationScheme)
        transmittedWave1 = []
        transmittedWave2 = []
        
        for symbol in range(len(symbols)/2):
            s0 = symbols[2*symbol]
            s1 = symbols[2*symbol + 1]
        
            wave1 = transmitter1.CreateWaveForSymbol(s0)
            wave2 = transmitter2.CreateWaveForSymbol(s1)
            
            #Appends the waveform to the LEFT 
            transmittedWave1[0:0]=wave1
            transmittedWave2[0:0]=wave2
            
            s1ConjugateNegative = -s1.conjugate()
            s0Conjugate = s0.conjugate()
            
            wave3 = transmitter1.CreateWaveForSymbol(s1ConjugateNegative)
            wave4 = transmitter2.CreateWaveForSymbol(s0Conjugate)
            
            transmittedWave1[0:0]=wave3
            transmittedWave2[0:0]=wave4
        