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

class Simulation():
    def __init__(self):
        self.rwControl = FileManager.FileManager()
    
    def Run(self, binInput, modulationScheme, noiseDeviation = 0.05, transmitPower = 1, estimationMethod = None, decoderType = DecoderType.ML):
        binOutput = ''
        binInput = self.PadBinary(binInput,modulationScheme)
        rec = Receiver()
        al = AlamoutiScheme(transmitPower)
        inputStrings = self.SplitInput(binInput)
        progress = 0.0
        self.progressInt = 0
        
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
    
                output = rec.AlamoutiCombine(h0,h1,r0,r1)
              
                #Detection/Demodulation
                if decoderType == DecoderType.ML:
                    binOutput += rec.MLDSymbolToBinary(output[0], modulationScheme,transmitPower)
                    binOutput += rec.MLDSymbolToBinary(output[1], modulationScheme,transmitPower)
                # else use sphere detection

                progress = float(len(binOutput))/float(len(binInput))
                #.progressInt = int(progress)
                print progress

        numErrors = 0

        for n in range(len(binInput)):
            if binInput[n] != binOutput[n]:
                numErrors += 1
                
        self.BinaryToImage(binOutput)
                
        BER = float(numErrors) /  float(len(binInput))     
        res = SimulationResults(binOutput, BER, numErrors)
        return res
    
    def CreateBinaryStream(self, length):
        random.seed()
        bs = ''
        for n in range(length):
            bs += str(random.randint(0,1))
        return bs
    
    def ImageToBinary(self, path = getcwd() + '\AppData' + '\\' + 'PH_image.png'):
        self.rwControl.ReadFile(path)
        return self.rwControl.imageBinaryStr
    
    def BinaryToImage(self, binString):
        imageData = self.rwControl.BinStrToPBytes(self.rwControl.imageBinaryStr)
        self.rwControl.WriteFile(imageData)
    
    def WriteGraphToFile(self, graph, newFileName, fileLocation = GlobalSettings.imageFolderPath):
        print "Creating File"
        
    def PadBinary(self, binInput, ModType):
        if(ModType == ModulationType.BPSK and len(binInput)%2 != 0):
            binInput+= '0'
        elif(ModType == ModulationType.QPSK and len(binInput)%4 != 0):
            for i in range(len(binInput)%4):
                binInput+= '0'
        elif(ModType == ModulationType.QAM16 and len(binInput)%8 != 0):
            for i in range(len(binInput)%8):
                binInput+= '0'
        elif(ModType == ModulationType.QAM64 and len(binInput)%12 != 0):
            for i in range(len(binInput)%8):
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
    def __init__(self, outputBin, BER, numErrors):
        self.output = outputBin
        self.BER = BER
        self.numErrors = numErrors

