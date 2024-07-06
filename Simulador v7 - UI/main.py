import PySimpleGUI as sg
import simulatorUI
import creatureUI
import actionUI
import conditionUI
import resourcesUI
from utilitiesUI import *

# Define layouts for different views

layout_main = [
    [[sg.TabGroup([[sg.Tab('Simulator',simulatorUI.layout_simulator), sg.Tab('Creatures',creatureUI.layout_creatures), sg.Tab('Actions',actionUI.layout_actions), sg.Tab('Conditions',conditionUI.layout_conditions), sg.Tab('Resources', resourcesUI.layout_resources)]])]]
]

main_window = sg.Window('D&D Simulator', layout_main, ttk_theme=ttk_style, resizable=True, finalize=True)
secondary_window = None

#set_invisible
main_window['_TEAM3COLUMN_'].update(visible=False)
main_window['_TEAM4COLUMN_'].update(visible=False)

# Event loop
while True:
    window, event, values = sg.read_all_windows()
    #Closing Event
    if event == sg.WIN_CLOSED:
        window.close()
        if window == main_window:
            break
        else:
            window = None
    print(event) 
    
    simulatorUI.events(event,values,window,main_window,secondary_window)
    creatureUI.events(event,values,window,main_window,secondary_window)
    actionUI.events(event,values,window,main_window,secondary_window)
    conditionUI.events(event,values,window,main_window,secondary_window)
    resourcesUI.events(event,values,window,main_window,secondary_window)
    
        
main_window.close()