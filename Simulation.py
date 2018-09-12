from AlamoutiScheme import AlamoutiScheme
from FadingChannel import FadingChannel
from Receiver import Receiver
from OSTBCEnums import ModulationType, MultiplexerType, DecoderType
import GlobalSettings
import random
import Multiplexer as Multiplexer
import Demultiplexer as Demultiplexer
import FileManager as FileManager
from os import getcwd
from copy import deepcopy
import matplotlib.pyplot as plot

class Simulation():
    def __init__(self):
        self.rwControl = FileManager.FileManager()
        self.progressInt = 0
    
    def Run2by1(self, binInput, modulationScheme, noiseDeviation = 0.05, transmitPower = 1, estimationMethod = None, decoderType = DecoderType.ML):
        binOutput = ''
        binInput = self.PadBinary(binInput,modulationScheme)
        rec = Receiver()
        al = AlamoutiScheme(transmitPower)
        numTransmissions = 0
        hData = []
        inputStrings = self.SplitInput(binInput)
        progress = 0.0
        self.progressInt = 0
        
        for binString in inputStrings:
            transmissions = al.CreateTransmissions(binString,modulationScheme)
              
            for n in range(len(transmissions[0])/2):
                
                ch0 = FadingChannel(noiseDeviation)
                ch1 = FadingChannel(noiseDeviation)
                
                hData.append(abs(ch0.h))
                
                if(estimationMethod == None):
                    transmissionEx = deepcopy(transmissions[0][0]).wave  
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
                    if n == 0:
                        transmissionEx = deepcopy(transmissions[0][0]).wave   
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
                    h0 = Demux1.h0
                    h1 = Demux1.h1

                #Combining
    
                output = rec.AlamoutiCombine2by1(h0,h1,r0,r1)

                #Detection/Demodulation
                if decoderType == DecoderType.ML:
                    binOutput += rec.MLDSymbolToBinary(output[0], modulationScheme,transmitPower)
                    binOutput += rec.MLDSymbolToBinary(output[1], modulationScheme,transmitPower)
                # else use sphere detection
                
                numTransmissions +=4

                progress = float(len(binOutput))/float(len(binInput))
                self.progressInt = int(progress * 1000)
               

        numErrors = 0

        for n in range(len(binInput)):
            if binInput[n] != binOutput[n]:
                numErrors += 1
                
        self.BinaryToImage(binOutput)     
        
        BER = float(numErrors) /  float(len(binInput))     
        res = SimulationResults(binOutput, BER, len(binInput), numErrors, numTransmissions, hData, transmissionEx)
        return res
    
    def Run2by2(self, binInput, modulationScheme, noiseDeviation = 0.05, transmitPower = 1, estimationMethod = None, decoderType = DecoderType.ML):
        binOutput = ''
        binInput = self.PadBinary(binInput,modulationScheme)
        rec = Receiver()
        rec2 = Receiver()
        al = AlamoutiScheme(transmitPower)
        numTransmissions = 0
        hData = []
        inputStrings = self.SplitInput(binInput)
        progress = 0.0
        self.progressInt = 0
        
        for binString in inputStrings:
            
            transmissions = al.CreateTransmissions(binString,modulationScheme)
            transmissionEx = deepcopy(transmissions[0][0]).wave  
            #transmissions that will go to receiver 2
            transmissions2 = deepcopy(transmissions)
            
            for n in range(len(transmissions[0])/2):

                ch0 = FadingChannel(noiseDeviation)
                ch1 = FadingChannel(noiseDeviation)
                ch2 = FadingChannel(noiseDeviation)
                ch3 = FadingChannel(noiseDeviation)
                
                hData.append(abs(ch0.h))
                
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
                    if n == 0:
                        transmissionEx = deepcopy(transmissions[0][0]).wave  
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

                numTransmissions +=4
                progress = float(len(binOutput))/float(len(binInput))
                self.progressInt = int(progress*1000)


        numErrors = 0

        for n in range(len(binInput)):
            if binInput[n] != binOutput[n]:
                numErrors += 1
                
        self.BinaryToImage(binOutput)
                
        BER = float(numErrors) /  float(len(binInput))     
        res = SimulationResults(binOutput, BER, len(binInput), numErrors, numTransmissions, hData, transmissionEx)
        return res
    
    def CreateBinaryStream(self, length):
        random.seed()
        bs = ''
        for n in range(length):
            bs += str(random.randint(0,1))
        return bs
    
    def ImageToBinary(self, path = getcwd() + '\AppData' + '\\' + 'PH_image.png'):
        self.rwControl.ReadFile(path, True, True)
        return self.rwControl.imageBinaryStr
    
    def BinaryToImage(self, binString):
        imageData = self.rwControl.BinStrToPBytes(binString, True)
        self.rwControl.WriteFile(imageData, True)
           
    def PadBinary(self, binInput, ModType):

        if(ModType == ModulationType.BPSK and len(binInput)%2 != 0):
            binInput+= '0'
        elif(ModType == ModulationType.QPSK and len(binInput)%4 != 0):
            for i in range(4-len(binInput)%4):
                binInput+= '0'
        elif(ModType == ModulationType.QAM16 and len(binInput)%8 != 0):
            for i in range(8-len(binInput)%8):
                binInput+= '0'
        elif(ModType == ModulationType.QAM64 and len(binInput)%12 != 0):
            for i in range(12-len(binInput)%12):
                binInput+= '0'
               
        return binInput
    
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
    def __init__(self, outputBin, BER, fileSize, numErrors, numTransmissions, graphMagH, transmissionEx):
        self.output = outputBin
        self.BER = BER
        self.fileSize = fileSize
        self.numErrors = numErrors
        self.numTransmissions = numTransmissions
        self.graphMagH = graphMagH
        self.transmissionEx = transmissionEx

