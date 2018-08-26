import Tkinter as tk
from PIL import ImageTk, Image
import tkMessageBox
import FadingChannel as Channel
from OSTBCEnums import ModulationType, MultiplexerType, DecoderType
from Simulation import Simulation, SimulationResults
import numpy as np
import GlobalSettings
from os import getcwd
import tkFileDialog 
import ttk

class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.resizable(width = False, height = False)
        self.title("OSTBC Simulation")
        self.enumDictionary = {
                "BPSK": ModulationType.BPSK,
                "QPSK": ModulationType.QPSK,
                "QAM16": ModulationType.QAM16,
                "QAM64": ModulationType.QAM64,
                "Assume Ideal": None,
                "Pilot with FDM": MultiplexerType.FDM,
                "Pilot with OFDM": MultiplexerType.OFDM,
                "Maximum Likelyhood": DecoderType.ML,
                "Sphere": DecoderType.Sphere
                
        }
        
        
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        leftFrame = tk.Frame(container)
        leftFrame.grid(row = 0, column = 0)
        rightFrame = tk.Frame(container)
        rightFrame.grid(row = 0, column = 1)
        
        #Left Frame
        optionsFrame = tk.Frame(leftFrame)
        optionsFrame.grid(row = 1, column = 0, padx = 10, pady = 20)
        
        #Options for simulation
        modTypeLabel = tk.Label(optionsFrame, text = "Modulation Scheme:")
        modTypeLabel.grid(row = 0,column = 0, padx = 5)
        modTypes = ["BPSK", "QPSK", "QAM16", "QAM64"]
        self.modType = tk.StringVar(self)
        self.modType.set(modTypes[0])
        modulationList = tk.OptionMenu(optionsFrame,self.modType,*modTypes)
        modulationList.grid(row =0, column =1, padx = 5, pady = 2)
        
        chanEstLabel = tk.Label(optionsFrame, text = "Channel Estimation Method:")
        chanEstLabel.grid(row = 1, column = 0, padx = 5)
        channelEstTypes = ["Assume Ideal", "Pilot with FDM", "Pilot with OFDM"]
        self.channelEstimationMethod = tk.StringVar(self)
        self.channelEstimationMethod.set(channelEstTypes[0])
        channelEstimateBox = tk.OptionMenu(optionsFrame,self.channelEstimationMethod, *channelEstTypes)
        channelEstimateBox.grid(row = 1, column = 1,padx = 5, pady = 2)
        
        SNRLabel = tk.Label(optionsFrame, text = "SNR(dB):")
        SNRLabel.grid(row = 2, column = 0, padx = 5)
        SNRValues = [30.0, 20.0, 10.0, 5.0, 4.0, 3.0,2.0 ,1.0]
        self.SNR = tk.DoubleVar(self)
        self.SNR.set(SNRValues[0])
        SNRBox = tk.OptionMenu(optionsFrame,self.SNR, *SNRValues)
        SNRBox.grid(row = 2, column = 1,padx = 5, pady = 2)
        
        decodeLabel = tk.Label(optionsFrame, text = "Decoding Scheme:")
        decodeLabel.grid(row = 3, column = 0, padx = 5)
        decodeTypes = ["Maximum Likelyhood", "Sphere"]
        self.decodeMethod = tk.StringVar(self)
        self.decodeMethod.set(decodeTypes[0])
        decodeBox = tk.OptionMenu(optionsFrame,self.decodeMethod, *decodeTypes)
        decodeBox.grid(row = 3, column = 1,padx = 5, pady = 2)
        
        RecNumLabel = tk.Label(optionsFrame, text = "Number of Receiver Antennae:")
        RecNumLabel.grid(row = 4, column = 0, padx = 5)
        RecNumValues = [1,2]
        self.RecNum = tk.IntVar(self)
        self.RecNum.set(RecNumValues[0])
        RecNumBox = tk.OptionMenu(optionsFrame,self.RecNum, *RecNumValues)
        RecNumBox.grid(row = 4, column = 1,padx = 5, pady = 2)
        #End of options
        
        #Display input Image
        origImageLabel = tk.Label(leftFrame, text = "Original Image :")
        origImageLabel.grid(row = 3, column = 0)
        img = self.OpenImage(getcwd() + '\AppData' + '\\' + 'PH_image.png')
        photo = ImageTk.PhotoImage(img)
        self.picLabel = tk.Label(master = leftFrame, image = photo)
        self.picLabel.image = photo # keep a reference!
        self.picLabel.grid(row = 4,column = 0, padx = 10, pady = 10)
        self.picLabel.bind('<Button-1>', self.OnClick)
        
        #Display output Image
        recImageLabel = tk.Label(rightFrame, text = "Received Image :")
        recImageLabel.grid(row = 3, column = 0)
        img2 = self.OpenImage(getcwd() + '\AppData' + '\\' + 'PH_image2.png')
        photo2 = ImageTk.PhotoImage(img2)
        self.picLabel2 = tk.Label(master = rightFrame, image = photo2)
        self.picLabel2.image = photo2 # keep a reference!
        self.picLabel2.grid(row = 4,column = 0, padx = 10, pady = 10)
        
        #Progress Bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack()
        self.progress["value"] = 0
        self.progress["maximum"] = 1000
        #https://stackoverflow.com/questions/42422139/how-to-easily-avoid-tkinter-freezing

        
        #Simulate Button
        simulateButton = tk.Button(leftFrame, text = "Simulate",command = lambda:self.RunSimulation())
        simulateButton.grid(row = 5,column = 0)
        
        
        #Right Frame
        
        self.dataLabel = tk.Label(rightFrame, text = "Data from the simulation will be displayed here")
        self.dataLabel.grid(row = 1,padx = 0)
        
    def RunSimulation(self):
        #Get input data
        try:
            modType = self.enumDictionary.get(self.modType.get())
            pilotType = self.enumDictionary.get(self.channelEstimationMethod.get())
            decoderType = self.enumDictionary.get(self.decodeMethod.get())
            SNR = self.SNR.get()
            noiseStandardDeviation = np.sqrt(np.power(10.0, (-1*SNR)))
            numReceivers = self.RecNum.get()
        except:
            print "Alert: Input Error"
 
        sim = Simulation()
        
        #Temporary input data

        binInput = sim.CreateBinaryStream(4800)
        binInput = sim.ImageToBinary(self.path)
    
        if numReceivers == 1:
            res = sim.Run2by1(binInput,modType,noiseStandardDeviation,1,pilotType,decoderType)
        elif numReceivers == 2:
            res = sim.Run2by2(binInput,modType,noiseStandardDeviation,1,pilotType,decoderType)     

        self.dataLabel.config(text = "BER: "+str(res.BER))
        self.OutputImage(sim)
        

    def GetInputData(self):
        modType = self.modType.get()
        return modType
    
    def OnClick(self, event=None):
        tk.filename = ""
        tk.filename = tkFileDialog.askopenfilename(initialdir = r'C:\Users\kitty\Documents\GitHub\LabProject\Upload Image Folder',title = "Select file",filetypes = (("jpeg files","*.jpg"),("jpeg files","*.jpeg"),("png files","*.png")))
        if(tk.filename != ""):
            img = ImageTk.PhotoImage(self.OpenImage(tk.filename))
            self.picLabel.configure(image=img)
            self.picLabel.image = img
        
    def OpenImage(self, path):
        self.path = path
        self.original = Image.open(path, 'r')
        width = 300
        perWidth = (width/float(self.original.size[0]))
        heightRatio = int((float(self.original.size[1])*float(perWidth)))
        resizedImage = self.original.resize((width, heightRatio),Image.ANTIALIAS)
        return resizedImage
    
    def OutputImage(self, sim):
        img = ImageTk.PhotoImage(self.OpenImage(getcwd() + '\Images' + '\\' + sim.rwControl.imageName))
        self.picLabel2.configure(image=img)
        self.picLabel2.image = img
        
        
    
GUI = GUI()
GUI.mainloop()