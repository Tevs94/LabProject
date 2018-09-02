import Tkinter as tk
from PIL import ImageTk, Image
from OSTBCEnums import ModulationType, MultiplexerType, DecoderType
from Simulation import Simulation
import numpy as np
from os import getcwd
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import tkFileDialog 
import ttk
import threading
import time

class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.resizable(width = False, height = False)
        self.title("OSTBC Simulation")
        self.protocol("WM_DELETE_WINDOW", self.CloseApp)
        self.sim = Simulation()
        self.enumDictionary = {
                "BPSK": ModulationType.BPSK,
                "QPSK": ModulationType.QPSK,
                "QAM16": ModulationType.QAM16,
                "QAM64": ModulationType.QAM64,
                "Assume Ideal": None,
                "Pilot with FDM": MultiplexerType.FDM,
                "Pilot with TDM": MultiplexerType.TDM,
                "Maximum Likelyhood": DecoderType.ML    
        }
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        leftFrame = tk.Frame(container)
        leftFrame.grid(row = 0, column = 0)
        rightFrame = tk.Frame(container)
        rightFrame.grid(row = 0, column = 1)
        
        #Left Frame
        optionsFrame = tk.Frame(leftFrame)
        optionsFrame.grid(row = 1, column = 0, padx = 10, pady = 10)
        
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
        channelEstTypes = ["Assume Ideal", "Pilot with FDM", "Pilot with TDM"]
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
        decodeTypes = ["Maximum Likelyhood"]
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
        self.path = getcwd() + '\AppData' + '\\' + 'PH_image.png'
        photo = ImageTk.PhotoImage(img)
        self.picLabel = tk.Label(master = leftFrame, image = photo)
        self.picLabel.image = photo # keep a reference!
        self.picLabel.grid(row = 4,column = 0, padx = 10, pady = 2)
        self.picLabel.bind('<Button-1>', self.OnClick)
        
        
        #Progress Bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack()
        self.progress["value"] = 0
        self.progress["maximum"] = 1000
        

        
        #Simulate Button
        self.simulateButton = tk.Button(leftFrame, text = "Simulate",command = lambda:self.RunSimulation())
        self.simulateButton.grid(row = 5,column = 0)
        
        
        #Right Frame
        #Display output Image
        self.resultsHeadingLabel = tk.Label(rightFrame, text = "Data from the simulation will be displayed here")
        self.resultsHeadingLabel.grid(row = 1,padx = 0 , pady = 25)
        
        self.sizeLabel = tk.Label(rightFrame, text = "File size(bits):")
        self.sizeLabel.grid(row = 2,padx = 0, pady = 2)
        
        self.numErrorsLabel = tk.Label(rightFrame, text = "Number of errors(bits):")
        self.numErrorsLabel.grid(row = 3,padx = 0)
        
        self.BERLabel = tk.Label(rightFrame, text = "BER:")
        self.BERLabel.grid(row = 4,padx = 0, pady = 2)
        
        self.numTransmissionsLabel = tk.Label(rightFrame, text = "Number of transmissions:")
        self.numTransmissionsLabel.grid(row = 5,padx = 0, pady = 2)
        
        emptyPadding = tk.Label(rightFrame)
        emptyPadding.grid(row = 6, pady = 4)
        
        recImageLabel = tk.Label(rightFrame, text = "Received Image :")
        recImageLabel.grid(row =7, column = 0, pady = 2)
        img2 = self.OpenImage(getcwd() + '\AppData' + '\\' + 'PH_image2.png')
        photo2 = ImageTk.PhotoImage(img2)
        self.picLabel2 = tk.Label(master = rightFrame, image = photo2)
        self.picLabel2.image = photo2 # keep a reference!
        self.picLabel2.grid(row = 8,column = 0, padx = 10, pady = 2)
        
        graphButtons = tk.Label(rightFrame)
        graphButtons.grid(row = 9, pady = 2)
        self.hGraphButton = tk.Button(graphButtons, text = "Show Graph of |H|", state = tk.DISABLED)
        self.hGraphButton.grid(row = 0,column = 0, pady = 0, padx = 2)
        self.transmissionExButton = tk.Button(graphButtons, text = "Show example of Transmission", state = tk.DISABLED)
        self.transmissionExButton.grid(row = 0,column = 1, pady = 0, padx = 2)
        
       
    def RunSimulation(self):
        #Get input data
        try:
            modType = self.enumDictionary.get(self.modType.get())
            pilotType = self.enumDictionary.get(self.channelEstimationMethod.get())
            decoderType = self.enumDictionary.get(self.decodeMethod.get())
            SNR = self.SNR.get()
            noiseStandardDeviation = np.sqrt(np.power(10.0, (-1*SNR/10.0)))
            numReceivers = self.RecNum.get()
        except:
            print "Alert: Input Error"
 
        binInput = self.sim.ImageToBinary(self.path)
        
        self.Refresh()
        simThread = SimulationThread(self, binInput, modType, noiseStandardDeviation, pilotType, decoderType, numReceivers, self.sim)
        simThread.start()
        meterThread = MeterThread(self,simThread)
        meterThread.start()
        
    def CloseApp(self):
        self.destroy()

    #This functon controls image selection and is called when the upload image slot on the gui is clicked
    def OnClick(self, event=None):
        tk.filename = ""
        tk.filename = tkFileDialog.askopenfilename(initialdir = getcwd() + '\Upload Image Folder',title = "Select file",filetypes = [("png files","*.png")])
        if(tk.filename != ""):
            self.path = tk.filename
            img = ImageTk.PhotoImage(self.OpenImage(tk.filename))
            self.picLabel.configure(image=img)
            self.picLabel.image = img
        
    #This function reads in an image then scales it to the desired size for displaying on the GUI
    def OpenImage(self, path):
        self.original = Image.open(path, 'r')
        width = 300
        perWidth = (width/float(self.original.size[0]))
        heightRatio = int((float(self.original.size[1])*float(perWidth)))
        resizedImage = self.original.resize((width, heightRatio),Image.ANTIALIAS)
        return resizedImage

    #This function is used update the output image of the GUI, if python cannot read the transmited file, it displayed a corrupted notification image
    def OutputImage(self, sim, show = False):
        try:
            img = ImageTk.PhotoImage(self.OpenImage(getcwd() + '\Images' + '\\' + sim.rwControl.imageName))
            if(show == True):
                self.original.show()
            self.picLabel2.configure(image=img)
            self.picLabel2.image = img
        except: 
            img2 = self.OpenImage(getcwd() + '\AppData' + '\\' + 'PH_image3.png')
            photo2 = ImageTk.PhotoImage(img2)
            self.picLabel2.configure(image=photo2)
            self.picLabel2.image = photo2
        sim.rwControl.ClearGlobals()

    #Updates Tkniter gui ever 0.5s to prevent the application crashing before simulation ends.
    def Refresh(self):
        self.update()
        self.after(500,self.Refresh)      
        
    def EnableSimulateButton(self, enabledBool):
        if enabledBool == True:
            self.simulateButton.configure(state = tk.NORMAL)
            self.simulateButton.configure(text = "Simulate")
        else:
            self.simulateButton.configure(text = "Running Simulation")
            self.simulateButton.configure(state = tk.DISABLED)
         
    def OutputData(self, simRes):
        self.resultsHeadingLabel.config(text = "Simulation Completed!")
        self.sizeLabel.config(text = "File size(bits): " + str(simRes.fileSize))
        self.numErrorsLabel.config(text = "Number of errors(bits): "+str(simRes.numErrors))
        self.BERLabel.config(text = "BER: "+str(simRes.BER))
        self.numTransmissionsLabel.config(text = "Number of transmissions: "+str(simRes.numTransmissions))
        self.hGraphButton.config(command = lambda:self.CreateGraphWindow("Magnitude of H", simRes.graphMagH,range(len(simRes.graphMagH))))
        self.hGraphButton.config(state = tk.NORMAL)
        self.transmissionExButton.config(command = lambda:self.CreateGraphWindow("Transmission example", simRes.transmissionEx,range(len(simRes.transmissionEx))))
        self.transmissionExButton.config(state = tk.NORMAL)
        
    def CreateGraphWindow(self, title, data, xAxisPoints):
        graphWindow = tk.Toplevel(self)
        fig = Figure(figsize=(5,4), dpi=100)
        subPlot = fig.add_subplot(111)
        subPlot.set_title(title)
        subPlot.plot(xAxisPoints,data)
        dataPlot = FigureCanvasTkAgg(fig, master=graphWindow)
        dataPlot.show()
        dataPlot.get_tk_widget().pack()        

#This is a threading class used to allow the loading bar to update without affecting the simulation thread
class MeterThread(threading.Thread):
    def __init__(self, GUI, simThread):
        threading.Thread.__init__(self)
        self.name = "meterThread"
        self.sim = simThread.sim
        self.GUI = GUI
        
    def run(self):
        self.close = False
        while self.close == False:
            self.GUI.progress["value"] = self.sim.progressInt
            time.sleep(0.2)
            if(self.sim.progressInt == 1000):
                self.GUI.progress["value"] = 1000
                self.close = True

        
    def ForceClose(self):
        self.close = True
        
#Tkinter locks up if multithread isnt used along with a refresh function after, this class puts simulation on a seperate thread.
class SimulationThread(threading.Thread):
    def __init__(self, GUI,binInput,modType,noiseStandardDeviation,pilotType,decoderType,numReceivers, simObject):
        threading.Thread.__init__(self)
        self.name = "simulationThread"
        self.GUI = GUI
        self.binInput = binInput
        self.modType = modType
        self.noiseStandardDeviation = noiseStandardDeviation
        self.pilotType = pilotType
        self.decoderType = decoderType
        self.numReceivers = numReceivers 
        self.sim = simObject
        
    def run(self):
        self.GUI.EnableSimulateButton(False)
        if(self.numReceivers == 1):
            res = self.sim.Run2by1(self.binInput,self.modType,self.noiseStandardDeviation,1,self.pilotType,self.decoderType)
        else:
            res = self.sim.Run2by2(self.binInput,self.modType,self.noiseStandardDeviation,1,self.pilotType,self.decoderType)
        self.GUI.OutputData(res)
        self.GUI.OutputImage(self.sim, False)
        self.GUI.EnableSimulateButton(True)

   

GUI = GUI()
GUI.mainloop()