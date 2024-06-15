import PySimpleGUI as sg
import simulatorUI
import creatureUI
import actionUI
import conditionUI
from utilitiesUI import *

# Define layouts for different views

layout_main = [
    [[sg.TabGroup([[sg.Tab('Simulator',simulatorUI.layout_simulator), sg.Tab('Creatures',creatureUI.layout_creatures), sg.Tab('Actions',actionUI.layout_actions), sg.Tab('Conditions',conditionUI.layout_conditions)]])]]
]

window = sg.Window('D&D Simulator', layout_main, ttk_theme=ttk_style, size=(1200, 800))  # Adjusted window size


# Event loop
while True:
    event, values = window.read()
    #Closing Event
    if event == sg.WIN_CLOSED:
        break
    print(event) 
    
    simulatorUI.events(event,values,window)
    creatureUI.events(event,values,window)
    actionUI.events(event,values,window)
    conditionUI.events(event,values,window)
    
        
window.close()