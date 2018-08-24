sampleTime = 0.0001
carrierFrequency = 10
messageFrequency = 1
multiplexCarrierFrequency = 10 * carrierFrequency
multiplexCarrierAmplitude = 1 #Am modulation can break if carrier amplitude is smaller then whats being carried
#Keep carrier frequency a multiple of message frequency for simplicity purposes
imageFolderPath = "images/"
#maximum bits that should be sent to the transmission creator function to reduce risk of RAM problems
maxBitsPerTransmission = 60

