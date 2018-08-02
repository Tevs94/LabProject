from AlamoutiScheme import AlamoutiScheme
from FadingChannel import FadingChannel
from Receiver import Receiver
from OSTBCEnums import ModulationType

class Simulation():
    def Run(self, binInput, modulationScheme, noiseDeviation = 0.1):
        binOutput = ''
        al = AlamoutiScheme()
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
            h0 = ch0.h
            h1 = ch1.h
            #Combining
            output = rec.AlamoutiCombine(h0,h1,r0,r1)
            #Detection/Demodulation
            binOutput += rec.MLDSymbolToBinary(output[0], modulationScheme)
            binOutput += rec.MLDSymbolToBinary(output[1], modulationScheme)
        print "Input:"
        print binInput
        print "Output:"
        print binOutput

binInput = '1111010110100000'
sim = Simulation()
sim.Run(binInput,ModulationType.QPSK)