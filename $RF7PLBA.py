#TEST SCRIPT
from AlamoutiScheme import AlamoutiScheme
from FadingChannel import FadingChannel
from Receiver import Receiver
from OSTBCEnums import ModulationType

binInput= '1111000010100101'
binOutput = ''
al = AlamoutiScheme()
transmissions = al.CreateTransmissions(binInput,ModulationType.QPSK)
rec = Receiver()
#transmissions[transmitter Number][transmission Number] 
for n in range(len(transmissions[0])/2):
    ch0 = FadingChannel(10)
    ch1 = FadingChannel(10)
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
    #Detection
    binOutput += rec.MLDSymbolToBinary(output[0],ModulationType.QPSK)
    binOutput += rec.MLDSymbolToBinary(output[1],ModulationType.QPSK)
print "Input:"
print binInput
print "Output:"
print binOutput