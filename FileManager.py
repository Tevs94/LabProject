from os import getcwd 
import binascii
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

class InvalidType(Exception):
    pass

#This class is used to handle image data
# image to binary and binary to image
class FileManager():
    def __init__(self):
        self.imageName = ''
        self.imageBinaryBytes = ''
        self.imageBinaryStr = ''
        self.preservedHeaderBytes = ''
        self.imageType = ''
        self.currentDirectory = getcwd()
        
    #Used to prevent error on multiple simulation runs with gui
    def ClearGlobals(self):
        self.imageName = ''
        self.imageBinaryBytes = ''
        self.imageBinaryStr = ''
        self.preservedHeaderBytes = ''
        self.imageType = ''
        self.byteLength = [0]
        
    #This function is used to read file data in as binary bytes
    #The function can handle any directory format that a windows application may spit out unless no root is provided.
    def ReadFile(self, location, pad = False, preserve = False):
        #NOTE!!!!!!!!!!!! Uses raw strings that mean start r
        if(location.endswith(('.jpeg', '.jpg', '.png'))):
            if '/' not in location: 
                pathElements = location.split('\\')
            else:
                pathElements = location.split('/')
            self.imageType = pathElements[-1][-3:]
            self.imageName = pathElements[-1]
        elif(location.endswith('"\"')):
            pathElements = location.split('"\"')
            if(pathElements[-2].endswith(('.jpeg', '.jpg', '.png'))):
                self.imageType = pathElements[-2][-3:]
                self.imageName = pathElements[-2]
            else:
                raise InvalidType()
        else:
            raise InvalidType()
        image = open(location, "rb")
        self.imageBinaryBytes = image.read()
        if(preserve == True):
            self.PreserveHeader()
        self.PBytesToBinStr(self.imageBinaryBytes, pad)
        image.close()
            
    #This function is used to preserve the first x bytes of a image file, without the likely hood of a completely corrupted image at a single bit error is higher then desired.
    def PreserveHeader(self):
        if(self.imageType == 'jpg' or self.imageType == 'jpeg'):
            self.preservedHeaderBytes = self.imageBinaryBytes[0:6]
            self.imageBinaryBytes = self.imageBinaryBytes[6:]
        else:
            self.preservedHeaderBytes = self.imageBinaryBytes[0:26] #png
            self.imageBinaryBytes = self.imageBinaryBytes[26:]
    
    #This function writes the binary bytes to a image file
    def WriteFile(self, binaryStream, preserve = False):
        if(preserve == True):
            binaryStream = self.preservedHeaderBytes + binaryStream
        image = open(self.currentDirectory + '\Images' + '\\' + self.imageName, 'wb')
        image.write(binaryStream)
        image.close()

    #This function is used to do the most protected form of data conversion from binary bytes to bytes, from multiple tests this is just the best solution.
    def PBytesToBinStr(self, PBytes, pad = False):
        self.byteLength = [0] * len(PBytes)
        for n in range(len(PBytes)):
#        for n in range(2):
            hexData = binascii.hexlify(PBytes[n])
            append0x = '0x'+hexData
            intData = int(append0x, 0)
            binData = self.BinaryHandler(intData, n, pad)
            self.imageBinaryStr += binData
    
    #As name say this handles char that make appear in int to hex conversion ensuring a clean conversion
    def IntToHex(self, intVal):
        hexData = hex(intVal)
        if(len(hexData) == 3):
            hexData = hexData[0:1]+'x0'+hexData[2]
            remove0x = hexData[2:]
        else:
            remove0x = hexData[2:]
        return remove0x
    
    #This function is used to pad the binary stream to ensure 8 bits per stream
    def BinaryHandler(self, intData, n, pad = False):
        binValue = bin(intData)
        binValue = binValue[2:]
        if(pad == True):
            if(len(binValue) != 8):
                for i in range(8 - len(binValue)):
                    binValue = '0'+binValue
        else:
            self.byteLength[n] = len(binValue)
        return binValue

    #This function performs the conversion chain needed to go from a raw binary stream to python binary byte
    def BinStrToPBytes(self, binStr, pad = False):
        byteList = bytes() 
        if(pad == False):
            index = 0
            for n in range(len(self.byteLength)):
                bitLength = self.byteLength[n]
                binByteData = binStr[index:index+bitLength]
                index+=bitLength
                reInt = int(binByteData, 2)
                binBytes = binascii.unhexlify(self.IntToHex(reInt))
                byteList += binBytes
            return byteList
        else:
            index = 0
            for n in range(len(binStr)/8):
                binByteData = binStr[index:index+8]
                index+=8
                reInt = int(binByteData, 2)
                binBytes = binascii.unhexlify(self.IntToHex(reInt))
#                if(n > 500):
#                    binBytes = binascii.unhexlify(self.IntToHex(255))
                byteList += binBytes
            return byteList
