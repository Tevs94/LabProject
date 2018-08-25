from AlamoutiScheme import AlamoutiScheme
from FadingChannel import FadingChannel
from Receiver import Receiver
from OSTBCEnums import ModulationType, MultiplexerType, DecoderType
import GlobalSettings
import random
import Multiplexer as Multiplexer
import Demultiplexer as Demultiplexer
from copy import deepcopy

class Simulation():
    def Run2by1(self, binInput, modulationScheme, noiseDeviation = 0.05, transmitPower = 1, estimationMethod = None, decoderType = DecoderType.ML):
        binOutput = ''
        rec = Receiver()
        al = AlamoutiScheme(transmitPower)
        inputStrings = self.SplitInput(binInput)
        progress = 0.0
        
        for binString in inputStrings:
            
            transmissions = al.CreateTransmissions(binString,modulationScheme)
                
            for n in range(len(transmissions[0])/2):

                ch0 = FadingChannel(noiseDeviation)
                ch1 = FadingChannel(noiseDeviation)
                   
                if(estimationMethod == None):
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
                                        
                else:
                    #Timeslot1
                    Mux10 = Multiplexer.Multiplexer(estimationMethod,transmissions[0][2*n])
                    Mux11 = Multiplexer.Multiplexer(estimationMethod,transmissions[1][2*n])
                    transmissions[0][2*n].OverideWave(Mux10.wave)
                    transmissions[1][2*n].OverideWave(Mux11.wave)
                    ch0.ApplyFadingToTransmission(transmissions[0][2*n])
                    ch1.ApplyFadingToTransmission(transmissions[1][2*n])
                    Demux1 = Demultiplexer.Demultiplexer(estimationMethod,transmissions[0][2*n].wave, transmissions[1][2*n].wave)
                    transmissions[0][2*n].OverideWave(Demux1.s0)
                    transmissions[1][2*n].OverideWave(Demux1.s1)
                    r0 = rec.CombineReceivedTransmissions(transmissions[0][2*n],transmissions[1][2*n])
                    #Timeslot2
                    Mux20 = Multiplexer.Multiplexer(estimationMethod,transmissions[0][(2*n)+1])
                    Mux21 = Multiplexer.Multiplexer(estimationMethod,transmissions[1][(2*n)+1])
                    transmissions[0][(2*n)+1].OverideWave(Mux20.wave)
                    transmissions[1][(2*n)+1].OverideWave(Mux21.wave)
                    ch0.ApplyFadingToTransmission(transmissions[0][(2*n)+1])
                    ch1.ApplyFadingToTransmission(transmissions[1][(2*n)+1])
                    Demux2 = Demultiplexer.Demultiplexer(estimationMethod,transmissions[0][(2*n)+1].wave, transmissions[1][(2*n)+1].wave)
                    transmissions[0][(2*n)+1].OverideWave(Demux2.s0)
                    transmissions[1][(2*n)+1].OverideWave(Demux2.s1)
                    r1 = rec.CombineReceivedTransmissions(transmissions[0][(2*n)+1],transmissions[1][(2*n)+1])
                    #Channel Estimation
                    h0 = Demux2.h0
                    h1 = Demux2.h1
                
                #Combining
    
                output = rec.AlamoutiCombine2by1(h0,h1,r0,r1)

                #Detection/Demodulation
                if decoderType == DecoderType.ML:
                    binOutput += rec.MLDSymbolToBinary(output[0], modulationScheme,transmitPower)
                    binOutput += rec.MLDSymbolToBinary(output[1], modulationScheme,transmitPower)
                # else use sphere detection

                progress = float(len(binOutput))/float(len(binInput))

        numErrors = 0

        for n in range(len(binInput)):
            if binInput[n] != binOutput[n]:
                numErrors += 1
                
        BER = float(numErrors) /  float(len(binInput))     
        res = SimulationResults(binOutput, BER, numErrors)
        return res
    
    def Run2by2(self, binInput, modulationScheme, noiseDeviation = 0.05, transmitPower = 1, estimationMethod = None, decoderType = DecoderType.ML):
        binOutput = ''
        rec = Receiver()
        rec2 = Receiver()
        al = AlamoutiScheme(transmitPower)
        inputStrings = self.SplitInput(binInput)
        progress = 0.0
        
        for binString in inputStrings:
            
            transmissions = al.CreateTransmissions(binString,modulationScheme)
            #transmissions that will go to receiver 2
            transmissions2 = deepcopy(transmissions)
            
            for n in range(len(transmissions[0])/2):

                ch0 = FadingChannel(noiseDeviation)
                ch1 = FadingChannel(noiseDeviation)
                ch2 = FadingChannel(noiseDeviation)
                ch3 = FadingChannel(noiseDeviation)
                   
                if(estimationMethod == None):
                    #Timeslot1
                    ch0.ApplyFadingToTransmission(transmissions[0][2*n])
                    ch1.ApplyFadingToTransmission(transmissions[1][2*n])
                    r0 = rec.CombineReceivedTransmissions(transmissions[0][2*n],transmissions[1][2*n])
                                       
                    ch2.ApplyFadingToTransmission(transmissions2[0][2*n])
                    ch3.ApplyFadingToTransmission(transmissions2[1][2*n])
                    r2 = rec2.CombineReceivedTransmissions(transmissions2[0][2*n],transmissions2[1][2*n]) 

                    #Timeslot2
                    ch0.ApplyFadingToTransmission(transmissions[0][(2*n)+1])
                    ch1.ApplyFadingToTransmission(transmissions[1][(2*n)+1])
                    r1 = rec.CombineReceivedTransmissions(transmissions[0][(2*n)+1],transmissions[1][(2*n)+1])
                    
                    ch2.ApplyFadingToTransmission(transmissions2[0][(2*n)+1])
                    ch3.ApplyFadingToTransmission(transmissions2[1][(2*n)+1])
                    r3 = rec2.CombineReceivedTransmissions(transmissions2[0][(2*n)+1],transmissions2[1][(2*n)+1]) 
                    #Channel Estimation
                    h0 = ch0.h
                    h1 = ch1.h
                    h2 = ch2.h
                    h3 = ch3.h 
                    
                else:
                    #Timeslot1
                    Mux10 = Multiplexer.Multiplexer(estimationMethod,transmissions[0][2*n])
                    Mux11 = Multiplexer.Multiplexer(estimationMethod,transmissions[1][2*n])
                    Mux12 = Multiplexer.Multiplexer(estimationMethod,transmissions2[0][2*n])
                    Mux13 = Multiplexer.Multiplexer(estimationMethod,transmissions2[1][2*n])
                    transmissions[0][2*n].OverideWave(Mux10.wave)
                    transmissions[1][2*n].OverideWave(Mux11.wave)
                    transmissions2[0][2*n].OverideWave(Mux12.wave)
                    transmissions2[1][2*n].OverideWave(Mux13.wave)
                    ch0.ApplyFadingToTransmission(transmissions[0][2*n])
                    ch1.ApplyFadingToTransmission(transmissions[1][2*n])
                    ch2.ApplyFadingToTransmission(transmissions2[0][2*n])
                    ch3.ApplyFadingToTransmission(transmissions2[1][2*n])
                    Demux1 = Demultiplexer.Demultiplexer(estimationMethod,transmissions[0][2*n].wave, transmissions[1][2*n].wave)
                    Demux3 = Demultiplexer.Demultiplexer(estimationMethod,transmissions2[0][2*n].wave, transmissions2[1][2*n].wave)
                    transmissions[0][2*n].OverideWave(Demux1.s0)
                    transmissions[1][2*n].OverideWave(Demux1.s1)
                    transmissions2[0][2*n].OverideWave(Demux3.s0)
                    transmissions2[1][2*n].OverideWave(Demux3.s1)
                    r0 = rec.CombineReceivedTransmissions(transmissions[0][2*n],transmissions[1][2*n])
                    r2 = rec2.CombineReceivedTransmissions(transmissions2[0][2*n],transmissions2[1][2*n])
                    #Timeslot2
                    Mux20 = Multiplexer.Multiplexer(estimationMethod,transmissions[0][(2*n)+1])
                    Mux21 = Multiplexer.Multiplexer(estimationMethod,transmissions[1][(2*n)+1])
                    Mux22 = Multiplexer.Multiplexer(estimationMethod,transmissions2[0][(2*n)+1])
                    Mux23 = Multiplexer.Multiplexer(estimationMethod,transmissions2[1][(2*n)+1])
                    transmissions[0][(2*n)+1].OverideWave(Mux20.wave)
                    transmissions[1][(2*n)+1].OverideWave(Mux21.wave)
                    transmissions2[0][(2*n)+1].OverideWave(Mux22.wave)
                    transmissions2[1][(2*n)+1].OverideWave(Mux23.wave)
                    ch0.ApplyFadingToTransmission(transmissions[0][(2*n)+1])
                    ch1.ApplyFadingToTransmission(transmissions[1][(2*n)+1])
                    ch2.ApplyFadingToTransmission(transmissions2[0][(2*n)+1])
                    ch3.ApplyFadingToTransmission(transmissions2[1][(2*n)+1])
                    Demux2 = Demultiplexer.Demultiplexer(estimationMethod,transmissions[0][(2*n)+1].wave, transmissions[1][(2*n)+1].wave)
                    Demux4 = Demultiplexer.Demultiplexer(estimationMethod,transmissions2[0][(2*n)+1].wave, transmissions2[1][(2*n)+1].wave)
                    transmissions[0][(2*n)+1].OverideWave(Demux2.s0)
                    transmissions[1][(2*n)+1].OverideWave(Demux2.s1)
                    transmissions2[0][(2*n)+1].OverideWave(Demux4.s0)
                    transmissions2[1][(2*n)+1].OverideWave(Demux4.s1)
                    r1 = rec.CombineReceivedTransmissions(transmissions[0][(2*n)+1],transmissions[1][(2*n)+1])
                    r3 = rec2.CombineReceivedTransmissions(transmissions2[0][(2*n)+1],transmissions2[1][(2*n)+1])
                    #Channel Estimation
                    h0 = Demux2.h0
                    h1 = Demux2.h1
                    h2 = Demux4.h0
                    h3 = Demux4.h1
                
                #Combining
    
                output = rec.AlamoutiCombine2by2([h0,h1,h2,h3],[r0,r1,r2,r3])

                #Detection/Demodulation
                if decoderType == DecoderType.ML:
                    binOutput += rec.MLDSymbolToBinary(output[0], modulationScheme,transmitPower)
                    binOutput += rec.MLDSymbolToBinary(output[1], modulationScheme,transmitPower)
                # else use sphere detection

                progress = float(len(binOutput))/float(len(binInput))

        numErrors = 0

        for n in range(len(binInput)):
            if binInput[n] != binOutput[n]:
                numErrors += 1
                
        BER = float(numErrors) /  float(len(binInput))     
        res = SimulationResults(binOutput, BER, numErrors)
        return res
    
    def CreateBinaryStream(self, length):
        random.seed()
        bs = ''
        for n in range(length):
            bs += str(random.randint(0,1))
        return bs
    
    def SplitInput(self, binInput):
        inputStrings = ['']
        numStrings = 0
        for bit in binInput:
            if len(inputStrings[numStrings]) < GlobalSettings.maxBitsPerTransmission:
                inputStrings[numStrings] += bit
            else:
                numStrings += 1
                inputStrings.append('')
                inputStrings[numStrings] += bit
        return inputStrings
    
class SimulationResults():
    #storage class for all the results of the simulation
    def __init__(self, outputBin, BER, numErrors):
        self.output = outputBin
        self.BER = BER
        self.numErrors = numErrors

