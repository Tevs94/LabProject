class InvalidType(Exception):
    print 'File must be type .jpg, .jpeg or .png'
    pass

class FileManager():
    def __init__(self):
        
    def OpenFile(self, location):
        try:
            path = location.resolve()
        except FileNotFoundError:
            raise NonBinaryInput()
        binaryData = open(location, 'rb')
        image = binaryData.read()
        binaryData.close()