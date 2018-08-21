import Tkinter as tk
from PIL import ImageTk, Image
import tkMessageBox
import FadingChannel as Channel
from OSTBCEnums import ModulationType, MultiplexerType, DecoderType
from Simulation import Simulation, SimulationResults
import GlobalSettings

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
        
        noiseLabel = tk.Label(optionsFrame, text = "Noise Variance:")
        noiseLabel.grid(row = 2, column = 0, padx = 5)
        self.noiseEntry = tk.Entry(optionsFrame)
        self.noiseEntry.grid(row = 2, column = 1, padx = 5, pady = 2)
        
        decodeLabel = tk.Label(optionsFrame, text = "Decoding Scheme:")
        decodeLabel.grid(row = 3, column = 0, padx = 5)
        decodeTypes = ["Maximum Likelyhood", "Sphere"]
        self.decodeMethod = tk.StringVar(self)
        self.decodeMethod.set(decodeTypes[0])
        decodeBox = tk.OptionMenu(optionsFrame,self.decodeMethod, *decodeTypes)
        decodeBox.grid(row = 3, column = 1,padx = 5, pady = 2)
        
        #End of options
        
        #Display input Image
        origImageLabel = tk.Label(leftFrame, text = "Original Image :")
        origImageLabel.grid(row = 2, column = 0)
        image = Image.open("testImage2.png")
        photo = ImageTk.PhotoImage(image)
        picLabel = tk.Label(master = leftFrame, image = photo)
        picLabel.image = photo # keep a reference!
        picLabel.grid(row = 3,column = 0, padx = 10, pady = 10)

               
        simulateButton = tk.Button(leftFrame, text = "Simulate",command = lambda:self.RunSimulation())
        simulateButton.grid(row = 4,column = 0)
        
        
        #Right Frame
        
        self.dataLabel = tk.Label(rightFrame, text = "Data from the simulation will be displayed here")
        self.dataLabel.grid(row = 1,padx = 30)
        
    def RunSimulation(self):
        #Get input data
        try:
            modType = self.enumDictionary.get(self.modType.get())
            pilotType = self.enumDictionary.get(self.channelEstimationMethod.get())
            decoderType = self.enumDictionary.get(self.decodeMethod.get())
            noiseDev = float(self.noiseEntry.get())
        except:
            print "Alert: Input Error"
 
        sim = Simulation()
        
        #Temporary input data
        binInput = sim.CreateBinaryStream(48*100)
        
        res = sim.Run(binInput,modType,noiseDev,1,pilotType,decoderType)
        self.dataLabel.config(text = "BER: "+str(res.BER))

    def GetInputData(self):
        modType = self.modType.get()
        return modType
    
GUI = GUI()
GUI.mainloop()
