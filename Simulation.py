from AlamoutiScheme import AlamoutiScheme
from FadingChannel import FadingChannel
from Receiver import Receiver
from OSTBCEnums import ModulationType, MultiplexerType, DecoderType
import GlobalSettings
import random

class Simulation():
    def Run(self, binInput, modulationScheme, noiseDeviation = 0.05, transmitPower = 1, estimationMethod = None, decoderType = DecoderType.ML):
        binOutput = ''
        al = AlamoutiScheme(transmitPower)
        transmissions = al.CreateTransmissions(binInput,modulationScheme)
        rec = Receiver()
        for n in range(len(transmissions[0])/2):
            ch0 = FadingChannel(noiseDeviation)
            ch1 = FadingChannel(noiseDeviation)
            #Timeslot1
            ch0.ApplyFadingToTransmission(transmissions[0][2*n])
            ch1.ApplyFadingToTransmission(transmissions[1][2*n])
            r0 = rec.CombineReceivedTransmissions(transmissions[0][2*n],transmissions[1][2*n])
            #Timeslot2
            ch0.ApplyFadingToTransmission(transmissions[0][(2*n)+1])
            ch1.ApplyFadingToTransmission(transmissions[1][(2*n)+1])
            r1 = rec.CombineReceivedTransmissions(transmissions[0][(2*n)+1],transmissions[1][(2*n)+1])
            
            #Channel Estimation
            if(estimationMethod == None):
                h0 = ch0.h
                h1 = ch1.h
            #else use piloting
            
            #Combining
            output = rec.AlamoutiCombine(h0,h1,r0,r1)
            
            #Detection/Demodulation
            if decoderType == DecoderType.ML:
                binOutput += rec.MLDSymbolToBinary(output[0], modulationScheme,transmitPower)
                binOutput += rec.MLDSymbolToBinary(output[1], modulationScheme,transmitPower)
            # else use sphere detection
            
        numErrors = 0
        for n in range(len(binInput)):
            if binInput[n] != binOutput[n]:
                numErrors += 1
                
        BER = float(numErrors) /  float(len(binInput))     
        res = SimulationResults(binOutput, BER)
        return res
    
    def CreateBinaryStream(self, length):
        random.seed()
        bs = ''
        for n in range(length):
            bs += str(random.randint(0,1))
        return bs
    
    def WriteGraphToFile(self, graph, newFileName, fileLocation = GlobalSettings.imageFolderPath):
        print "Creating File"

class SimulationResults():
    #storage class for all the results of the simulation
    def __init__(self, outputBin, BER):
        self.output = outputBin
        self.BER = BER

