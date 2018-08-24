from OSTBCEnums import ModulationType
import numpy as np
class ModulationConstellations():
    def __init__(self, a = 1):
        #Temporary normalization limits what the constellation power is
        a = 1
        self.BPSKDictionary = {
                        '0': [-a,0],
                        '1': [a,0]
                        }
        
        self.QPSKDictionary = {
                        '00': [-a,-a],
                        '01': [-a,a],
                        '10': [a,-a],
                        '11': [a,a],
                        }
         #https://slideplayer.com/slide/7618082/25/images/92/16-QAM+constellation+using+Gray+coding.jpg
        self.QAM16Dictionary = {
                           '0000': [-3*a,3*a],
                           '0001': [-3*a,a],
                           '0010': [-3*a,-3*a],
                           '0011': [-3*a,-a],
                           '0100': [-a,3*a],
                           '0101': [-a,a],
                           '0110': [-a,-3*a],
                           '0111': [-a,-a],
                           '1000': [3*a,3*a],
                           '1001': [3*a,a],
                           '1010': [3*a,-3*a],
                           '1011': [3*a,-a],
                           '1100': [a,3*a],
                           '1101': [a,a],
                           '1110': [a,-3*a],
                           '1111': [a,-a],
                           }
        self.QAM64Dictionary = {
                       '000000': [-7*a,-7*a],
                       '000001': [-7*a,-5*a],
                       '000010': [-7*a,-1*a],
                       '000011': [-7*a,-3*a],
                       '000100': [-7*a,7*a],
                       '000101': [-7*a,5*a],
                       '000110': [-7*a,1*a],
                       '000111': [-7*a,3*a],
                       '001000': [-5*a,-7*a],
                       '001001': [-5*a,-5*a],
                       '001010': [-5*a,-1*a],
                       '001011': [-5*a,-3*a],
                       '001100': [-5*a,7*a],
                       '001101': [-5*a,5*a],
                       '001110': [-5*a,1*a],
                       '001111': [-5*a,3*a],
                       
                       '010000': [-1*a,-7*a],
                       '010001': [-1*a,-5*a],
                       '010010': [-1*a,-1*a],
                       '010011': [-1*a,-3*a],
                       '010100': [-1*a,7*a],
                       '010101': [-1*a,5*a],
                       '010110': [-1*a,1*a],
                       '010111': [-1*a,3*a],
                       '011000': [-3*a,-7*a],
                       '011001': [-3*a,-5*a],
                       '011010': [-3*a,-1*a],
                       '011011': [-3*a,-3*a],
                       '011100': [-3*a,7*a],
                       '011101': [-3*a,5*a],
                       '011110': [-3*a,1*a],
                       '011111': [-3*a,3*a],
                       
                       '100000': [7*a,-7*a],
                       '100001': [7*a,-5*a],
                       '100010': [7*a,-1*a],
                       '100011': [7*a,-3*a],
                       '100100': [7*a,7*a],
                       '100101': [7*a,5*a],
                       '100110': [7*a,1*a],
                       '100111': [7*a,3*a],
                       '101000': [5*a,-7*a],
                       '101001': [5*a,-5*a],
                       '101010': [5*a,-1*a],
                       '101011': [5*a,-3*a],
                       '101100': [5*a,7*a],
                       '101101': [5*a,5*a],
                       '101110': [5*a,1*a],
                       '101111': [5*a,3*a],
                       
                       '110000': [1*a,-7*a],
                       '110001': [1*a,-5*a],
                       '110010': [1*a,-1*a],
                       '110011': [1*a,-3*a],    
                       '110100': [1*a,7*a],
                       '110101': [1*a,5*a],
                       '110110': [1*a,1*a],
                       '110111': [1*a,3*a],
                       '111000': [3*a,-7*a],
                       '111001': [3*a,-5*a],
                       '111010': [3*a,-1*a],
                       '111011': [3*a,-3*a],
                       '111100': [3*a,7*a],
                       '111101': [3*a,5*a],
                       '111110': [3*a,1*a],
                       '111111': [3*a,3*a],
                       }
        
        self.NormalizeConstellations()
        
    def GetConstellationDictionary(self, modulationScheme):
        if(modulationScheme == ModulationType.BPSK):
            return self.BPSKDictionary
        elif(modulationScheme == ModulationType.QPSK):
            return self.QPSKDictionary
        elif(modulationScheme == ModulationType.QAM16):
            return self.QAM16Dictionary
        elif(modulationScheme == ModulationType.QAM64):
            return self.QAM64Dictionary
    
    def NormalizeConstellations(self):
        for constellation in [self.BPSKDictionary , self.QPSKDictionary, self.QAM16Dictionary, self.QAM64Dictionary]:
            vals = constellation.values()
            totalPower = 0
            for point in vals:
                totalPower += np.sqrt(np.square(point[0])+np.square(point[1]))
            avgPower = totalPower/len(vals)
            for kvp in constellation:
                constellation[kvp][0] = constellation[kvp][0]/avgPower
                constellation[kvp][1] = constellation[kvp][1]/avgPower             
      