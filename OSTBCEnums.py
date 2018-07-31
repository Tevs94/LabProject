from enum import Enum

class ModulationType(Enum):
    BPSK = 1
    QPSK = 2
    QAM16 = 3
    QAM64 = 4
    
class MultiplexerType(Enum):
    FDM = 1
    OFDM = 2

    
