#SNR BER Graph Generating Script
#Line 15 and 106 of Simulation must be commented out
from OSTBCEnums import ModulationType, MultiplexerType, DecoderType
from Simulation import Simulation
import numpy as np
import matplotlib.pyplot as plot


sim = Simulation()
binInput = sim.CreateBinaryStream(9600)
SNRs = [0,2.5,5,7.5,10,12.5,15,17.5,20,22.5,25,27.5,30,32.5,35]
#SNRs = [0,2,3,4,5,7.5,10,12.5,15,17.5,20,22.5,25]
encodingSchemes = [ModulationType.BPSK, ModulationType.QPSK, ModulationType.QAM16, ModulationType.QAM64]
BERs = {
        ModulationType.BPSK:[],
        ModulationType.QPSK:[],
        ModulationType.QAM16:[],
        ModulationType.QAM64:[]
        }
#2 by 1 no estimation
for scheme in encodingSchemes:
    for SNR in SNRs:
        noiseDeviation  = np.sqrt(np.power(10.0, (-1*SNR/10.0)))
        simRes = sim.Run2by2(binInput, scheme, noiseDeviation, 1,MultiplexerType.TDM)
        BERs[scheme].append(simRes.BER)
        print "Inner"
    print "Outer"
        
        
        
fig, ax = plot.subplots()

ax.axis([0, 35, 10.0*np.power(10.0,-7), 1])
ax.set_xlabel("SNR(dB)")
ax.set_ylabel("BER")
ax.set_yscale('log')
bpsk = plot.plot(SNRs, BERs.get(ModulationType.BPSK), 'g', marker = "^")
qpsk = plot.plot(SNRs, BERs.get(ModulationType.QPSK), 'b', marker = "v")
qam16 = plot.plot(SNRs, BERs.get(ModulationType.QAM16), 'm', marker = ">")
qam64 = plot.plot(SNRs, BERs.get(ModulationType.QAM64), 'r', marker = "<")
ax.legend(["BPSK","QPSK", "QAM16", "QAM64"])

