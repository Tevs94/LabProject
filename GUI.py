import Tkinter as tk
import tkMessageBox
import FadingChannel as Channel
from OSTBCEnums import ModulationType

class GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("OSTBC Simulation")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        self.frame = tk.Frame()
        self.frame.grid()
        self.channel = Channel.FadingChannel(-1,1,1)
        simulateButton = tk.Button(self.frame, text = "Simulate",command = lambda:self.RunSimulation(self.GetInputData(), ModulationType.BPSK))
        simulateButton.grid()
        
    def RunSimulation(self, transmitData, modulationScheme):
        output = self.channel.PropogateInput(transmitData)
        return output
     
    def GetInputData(self):
        return 1
    
GUI = GUI()
GUI.mainloop()
