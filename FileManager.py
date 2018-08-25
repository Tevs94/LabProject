from os import getcwd 
import binascii

class InvalidType(Exception):
    pass

class FileManager():
    def __init__(self):
        self.imageName = ''
        self.imageBinaryBytes = ''
        self.imageBinaryStr = ''
        self.imageType = ''
        self.currentDirectory = getcwd()
        
    def ReadFile(self, location, pad = False):
        #NOTE!!!!!!!!!!!! Uses raw strings that mean start r
        if(location.endswith(('.jpeg', '.jpg', '.png'))):
            pathElements = location.split('\\')
            self.imageType = pathElements[-1][-3:]
            self.imageName = pathElements[-1]
            image = open(location, 'rb')
            self.imageBinaryBytes = image.read()
            self.PBytesToBinStr(self.imageBinaryBytes, pad)
            image.close()
            
        elif(location.endswith('"\"')):
            pathElements = location.split('"\"')
            if(pathElements[-2].endswith(('.jpeg', '.jpg', '.png'))):
                self.imageType = pathElements[-2][-3:]
                self.imageName = pathElements[-2]
                image = open(location, 'rb')
                self.imageBinaryBytes = image.read()
                self.PBytesToBinStr(self.imageBinaryBytes, pad)
                image.close()
            else:
                raise InvalidType()
        else:
            raise InvalidType()
        
    def WriteFile(self, binaryStream):
        image = open(self.currentDirectory + '\Images' + '\\' + self.imageName, 'wb')
        image.write(binaryStream)
        image.close()

    def PBytesToBinStr(self, PBytes, pad = False):
        self.byteLength = [0] * len(PBytes)
        for n in range(len(PBytes)):
#        for n in range(2):
            hexData = binascii.hexlify(PBytes[n])
            append0x = '0x'+hexData
            intData = int(append0x, 0)
            binData = self.BinaryHandler(intData, n, pad)
            self.imageBinaryStr += binData
        
    def IntToHex(self, intVal):
        hexData = hex(intVal)
        if(len(hexData) == 3):
            hexData = hexData[0:1]+'x0'+hexData[2]
            remove0x = hexData[2:]
        else:
            remove0x = hexData[2:]
        return remove0x
    
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
                byteList += binBytes
            return byteList

        
        
#test = FileManager()
#test.ReadFile(r"C:\Users\kitty\Documents\GitHub\LabProject\testImage.png", True)
#imageData = test.BinStrToPBytes(test.imageBinaryStr, True)
#print imageData == test.imageBinaryBytes
##print test.imageBinaryBytes
#test.WriteFile(imageData)
