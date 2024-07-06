import PySimpleGUI as sg
import os
from utilitiesUI import save, load, get_resources_list
import copy


#Resources

layout_resources_editor = [
    [sg.Text("Resource Names")],
    [sg.Input(size=(30,1), key='_RESOURCENAME_', justification='left', enable_events=True)],
    [sg.Button('Add Resource Name', use_ttk_buttons=True), sg.Button('Delete Resource Name', use_ttk_buttons=True)],
    [sg.Listbox(values=get_resources_list(), size=(50, 20), key='_ResourceNamesList_')],
    [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Resource Names')],
]

layout_resources = [
    [sg.VPush()],
    [sg.Push(), sg.Column(layout_resources_editor), sg.Push()],
    [sg.VPush()],
]

#Resource Events
def events(event,values,window,main_window,secondary_window):
    if event == 'Add Resource Name':
        resource_data = window['_ResourceNamesList_'].get_list_values()
        resource_data.append(values['_RESOURCENAME_'])
        window['_ResourceNamesList_'].update(resource_data)
    elif event == 'Delete Resource Name' and values['_ResourceNamesList_']:
        selected_resource = values['_ResourceNamesList_'][0]
        resource_data = window['_ResourceNamesList_'].get_list_values()
        resource_data.remove(selected_resource)
        window['_ResourceNamesList_'].update(resource_data)
        #creature_data['Combos'] = window['_ComboList_'].get_list_values()
    elif event == 'Save Resource Names':
        save(os.path.join(os.getcwd(), 'Resources/Resources.json'), window['_ResourceNamesList_'].get_list_values())