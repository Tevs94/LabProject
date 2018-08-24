from os import getcwd 
from struct import unpack, pack

class InvalidType(Exception):
    pass

class FileManager():
    def __init__(self):
        self.imageName = ''
        self.imageBinaryBytes = ''
        self.imageBinaryStr = ''
        self.imageType = ''
        self.currentDirectory = getcwd()
        
    def ReadFile(self, location):
        #NOTE!!!!!!!!!!!! Uses raw strings that mean start r
        if(location.endswith(('.jpeg', '.jpg', '.png'))):
            pathElements = location.split('\\')
            print pathElements
            self.imageType = pathElements[-1][-3:]
            self.imageName = pathElements[-1]
            image = open(location, 'rb')
            self.imageBinaryBytes = bytearray(image.read())
            self.PBytesToBinStr(self.imageBinaryBytes)
            image.close()
            
        elif(location.endswith('"\"')):
            pathElements = location.split('"\"')
            if(pathElements[-2].endswith(('.jpeg', '.jpg', '.png'))):
                self.imageType = pathElements[-2][-3:]
                self.imageName = pathElements[-2]
                binaryData = open(location, 'rb')
                self.imageBinary = binaryData.read()
                binaryData.close()
            else:
                raise InvalidType()
        else:
            raise InvalidType()
        
    def WriteFile(self, binaryStream):
        image = open(self.currentDirectory + '\Images' + '\\' + self.imageName, 'wb')
        image.write(binaryStream)
        image.close()

    def PBytesToBinStr(self, PBytes):
        fullString = ""
        for i in range(len(PBytes)):
            tmpBin = bin(PBytes[i])
            tmpStr = str(tmpBin[2:10]) #removes 0b
            fullString+=tmpStr
        self.imageBinaryStr = fullString
        
    def BinStrToPBytes(self, BinStr):
        binBytes = [BinStr[i:i+8] for i in range(0, len(BinStr), 8)]
        fixedBinStr = ['0b' + s for s in binBytes]
        intList = [0] * len(fixedBinStr)
        for i in range(len(fixedBinStr)):
            tmpInt = int(fixedBinStr[i], 2)
            intList[i]+=tmpInt
        return bytearray(intList)

        
        
#test = FileManager()
#test.ReadFile(r"C:\Users\kitty\Documents\GitHub\LabProject\testImage.png")
#print test.imageName
#print test.imageType
#print test.imageBinaryStr
#print "Total bit count: ", len(test.imageBinaryStr)
#print test.BinStrToPBytes(test.imageBinaryStr)

#print test.imageBinaryBytes
#test.WriteFile(bytes(test.BinStrToPBytes(test.imageBinaryStr)))
