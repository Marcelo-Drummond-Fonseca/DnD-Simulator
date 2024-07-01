import PySimpleGUI as sg
import os
from utilitiesUI import get_conditions_list, condition_end_possibilities, damage_types, save, load
import copy

#CONDITIONS


layout_condition_statistics = [
    [sg.VPush()],
    [sg.Text("Name", size=(4, 1)), sg.Input(size=(50, 1), key='_CONDITIONNAME_', justification='left', enable_events=True)],
    [sg.Text("Duration", size=(8,1)), sg.DropDown([1,2,10,100,'Permanent'], size=(5,1), key='_DURATION_'), 
    sg.Text('Turns, ends on', size=(14,1)), sg.DropDown(values=condition_end_possibilities, key='_ENDTYPE_')],
    [sg.Text("Paired Condition?"), sg.Checkbox('',default=False, key='_PAIREDCONDITION_')],
    [sg.Text("Hint: A Paired Condition has its effects applied on the caster.\nThese condition's effects apply only when considering interactions between caster and target.\nUsed for things like hiding, hunter's mark, etc.")],
    [sg.VPush()],
]

layout_condition_offenses = [
    [sg.VPush()],
    [sg.Text("Attack modifier", size=(15,1)), sg.Input(size=(3,1), key='_ATTACKMOD_'), 
    sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ATTACKADVANTAGE_'),
    sg.Text("Damage modifier", size=(15,1)), sg.Input(size=(3,1), key='_DAMAGEMOD_'),
    sg.Text("Crits on:", size=(8,1)), sg.Input(size=(3,1), key='_CRITSON_')],
    [sg.Text("Extra Damage")],
    [sg.Text("Damage (XdY+Z)", size=(13, 1)), sg.Input(size=(10, 1), key='_EXTRADAMAGEROLL_'), sg.DropDown(values=damage_types, key='_EXTRADAMAGETYPE_')],
    [sg.VPush()],
]

layout_condition_defenses = [
    [sg.VPush()],
    [sg.Text("AC modifier", size=(11,1)), sg.Input(size=(3,1), key='_ACMOD_'),
    sg.Text("Attacks against made at", size=(23,1)), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_DEFENSEADVANTAGE_')],
    [sg.Text("Auto crit?", size=(10,1)), sg.Checkbox('', key='_AUTOCRIT_', default=False)],
    [sg.Text("Saving Throw Modifiers", size=(21,1))],
    [sg.Text("STR", size=(3,1)), sg.Input(size=(3,1), key='_ST1MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST1ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.Checkbox('', key='_ST1EVASION_', default=False)],
    [sg.Text("DEX", size=(3,1)), sg.Input(size=(3,1), key='_ST2MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST2ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.Checkbox('', key='_ST2EVASION_', default=False)],
    [sg.Text("CON", size=(3,1)), sg.Input(size=(3,1), key='_ST3MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST3ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.Checkbox('', key='_ST3EVASION_', default=False)],
    [sg.Text("INT", size=(3,1)), sg.Input(size=(3,1), key='_ST4MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST4ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.Checkbox('', key='_ST4EVASION_', default=False)],
    [sg.Text("WIS", size=(3,1)), sg.Input(size=(3,1), key='_ST5MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST5ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.Checkbox('', key='_ST5EVASION_', default=False)],
    [sg.Text("CHA", size=(3,1)), sg.Input(size=(3,1), key='_ST6MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST6ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.Checkbox('', key='_ST6EVASION_', default=False)],
    [sg.Text("Resistances/Immunities/Vulnerabilities")],
    [sg.DropDown(values=damage_types, key='_DAMAGETYPERESISTANCEMOD_'), sg.Combo(values=['Resistance','Immunity','Vulnerability'], key='_RESISTANCETYPEMOD_')],
    [sg.Button('Add Resistance/Vulnerability/Immunity Modifier', use_ttk_buttons=True), sg.Button('Delete Resistance/Vulnerability/Immunity Modifier', use_ttk_buttons=True)],
    [sg.Listbox(values=[], size=(50, 5), key='_ResistanceModList_')],
    [sg.VPush()],
]

layout_condition_economy = [
    [sg.VPush()],
    [sg.Text("Amount modifiers",size=(16,1))],
    [sg.Text("Actions",size=(7,1)), sg.Input(size=(3,1), key='_ACTIONMOD_'),
    sg.Text("Bonus actions",size=(13,1)), sg.Input(size=(3,1), key='_BONUSACTIONMOD_'),
    sg.Text("Reactions",size=(9,1)), sg.Input(size=(3,1), key='_REACTIONMOD_')],
    [sg.VPush()],
]

layout_condition_over_time = [
    [sg.VPush()],
    [sg.Text("Damage over time")],
    [sg.Text("Damage (XdY+Z)", size=(13, 1)), sg.Input(size=(10, 1), key='_DAMAGEOVERTIMEROLL_'), sg.DropDown(values=damage_types, key='_DAMAGEOVERTIMETYPE_')],
    [sg.Text("Healing over time (XdY+Z)"), sg.Input(size=(10, 1), key='_HEALINGOVERTIMEROLL_')],
    [sg.VPush()],
]

layout_conditions_stats = [
    [sg.TabGroup([[sg.Tab('Basics',layout_condition_statistics),
    sg.Tab('Offenses',layout_condition_offenses),
    sg.Tab('Defenses',layout_condition_defenses),
    sg.Tab('Action Economy',layout_condition_economy),
    sg.Tab('Over Time Effects',layout_condition_over_time)]])],
    [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Condition'),
    sg.Button('Load', size=(10, 1), use_ttk_buttons=True, key='Load Condition')]
]

layout_conditions_sidebar = [
    [sg.Text('Conditions')],
    [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTCONDITION_', enable_events=True)],
    [sg.Listbox(values=get_conditions_list(), size=(20, 30), key='_CONDITIONS_', enable_events=True)],
    [sg.Button('Create New', use_ttk_buttons=True, key='Create New Condition')]
]

layout_conditions = [
    [sg.Column(layout_conditions_sidebar, element_justification='c'), sg.VerticalSeparator(), sg.Column(layout_conditions_stats)]
]

#CONDITION DATA

base_condition_data = {
    'Name': 'New Condition',
    'End Type': '',
    'Duration': '1',
    'Attack Modifier': '0',
    'Attack Advantage': '',
    'Crits On': '20',
    'Damage Modifier': '0',
    'Extra Damage Roll': '',
    'Extra Damage Type': '',
    'AC Modifier': '0',
    'Defense Advantage': '',
    'Auto Crit': False,
    'Saves Modifier': ['0','0','0','0','0','0'],
    'Saves Advantage': ['','','','','',''],
    'Resistances': [],
    'Action Modifier': '0',
    'Bonus Action Modifier': '0',
    'Reaction Modifier': '0',
    'Damage Over Time Roll': '',
    'Damage Over Time Type': '',
    'Healing Over Time': '',
    'Paired Condition': 'False',
    'Evasion': [False,False,False,False,False,False]
}    

condition_data = {
    'Name': None,
    'End Type': None,
    'Duration': None,
    'Attack Modifier': None,
    'Attack Advantage': None,
    'Crits On': None,
    'Damage Modifier': None,
    'Extra Damage Roll': None,
    'Extra Damage Type': None,
    'AC Modifier': None,
    'Defense Advantage': None,
    'Auto Crit': None,
    'Saves Modifier': [None,None,None,None,None,None],
    'Saves Advantage': [None,None,None,None,None,None],
    'Resistances': [],
    'Action Modifier': None,
    'Bonus Action Modifier': None,
    'Reaction Modifier': None,
    'Damage Over Time Roll': None,
    'Damage Over Time Type': None,
    'Healing Over Time': None,
    'Paired Condition': None,
    'Evasion': [None,None,None,None,None,None]
}

def update_condition(condition_data,window):
    window['_CONDITIONNAME_'].update(condition_data['Name'])
    window['_ENDTYPE_'].update(condition_data['End Type'])
    window['_DURATION_'].update(condition_data['Duration'])
    window['_ATTACKMOD_'].update(condition_data['Attack Modifier'])
    window['_ATTACKADVANTAGE_'].update(condition_data['Attack Advantage'])
    window['_CRITSON_'].update(condition_data['Crits On'])
    window['_DAMAGEMOD_'].update(condition_data['Damage Modifier'])
    window['_EXTRADAMAGEROLL_'].update(condition_data['Extra Damage Roll'])
    window['_EXTRADAMAGETYPE_'].update(condition_data['Extra Damage Type'])
    window['_ACMOD_'].update(condition_data['AC Modifier'])
    window['_DEFENSEADVANTAGE_'].update(condition_data['Defense Advantage'])
    window['_AUTOCRIT_'].update(condition_data['Auto Crit'])
    if 'Auto Crit' in condition_data: 
        if condition_data['Auto Crit'] == 'True':
            window['_AUTOCRIT_'].update(True)
        elif condition_data['Auto Crit'] == 'False':
            window['_AUTOCRIT_'].update(False)
        else: window['_AUTOCRIT_'].update(condition_data['Auto Crit'])
    for i in range(1, 7):
        window[f'_ST{i}MOD_'].update(condition_data['Saves Modifier'][i-1])
        window[f'_ST{i}ADVANTAGE_'].update(condition_data['Saves Advantage'][i-1])
        if 'Evasion' in condition_data: 
            if condition_data['Evasion'][i-1] == 'True':
                window[f'_ST{i}EVASION_'].update(True)
            elif condition_data['Evasion'][i-1] == 'False':
                window[f'_ST{i}EVASION_'].update(False)
            else: window[f'_ST{i}EVASION_'].update(condition_data['Evasion'][i-1])
        else: window[f'_ST{i}EVASION_'].update(False)
    window['_ResistanceModList_'].update(condition_data['Resistances'])
    window['_ACTIONMOD_'].update(condition_data['Action Modifier'])
    window['_BONUSACTIONMOD_'].update(condition_data['Bonus Action Modifier'])
    window['_REACTIONMOD_'].update(condition_data['Reaction Modifier'])
    window['_DAMAGEOVERTIMEROLL_'].update(condition_data['Damage Over Time Roll'])
    window['_DAMAGEOVERTIMETYPE_'].update(condition_data['Damage Over Time Type'])
    window['_HEALINGOVERTIMEROLL_'].update(condition_data['Healing Over Time'])
    if 'Paired Condition' in condition_data: 
        if condition_data['Paired Condition'] == 'True':
            window['_PAIREDCONDITION_'].update(True)
        elif condition_data['Paired Condition'] == 'False':
            window['_PAIREDCONDITION_'].update(False)
        else: window['_PAIREDCONDITION_'].update(condition_data['Paired Condition'])
    else: window['_PAIREDCONDITION_'].update(False)

def update_condition_data(values,window):
    condition_data['Name'] = values['_CONDITIONNAME_']
    condition_data['End Type'] = values['_ENDTYPE_']
    condition_data['Duration'] = values['_DURATION_']
    condition_data['Attack Modifier'] = values['_ATTACKMOD_']
    condition_data['Attack Advantage'] = values['_ATTACKADVANTAGE_']
    condition_data['Crits On'] = values['_CRITSON_']
    condition_data['Damage Modifier'] = values['_DAMAGEMOD_']
    condition_data['Extra Damage Roll'] = values['_EXTRADAMAGEROLL_']
    condition_data['Extra Damage Type'] = values['_EXTRADAMAGETYPE_']
    condition_data['AC Modifier'] = values['_ACMOD_']
    condition_data['Defense Advantage'] = values['_DEFENSEADVANTAGE_']
    condition_data['Auto Crit'] = values['_AUTOCRIT_']
    condition_data['Saves Modifier'] = [values[f'_ST{i}MOD_'] for i in range(1, 7)]
    condition_data['Saves Advantage'] = [values[f'_ST{i}ADVANTAGE_'] for i in range(1, 7)]
    condition_data['Evasion'] = [values[f'_ST{i}EVASION_'] for i in range(1, 7)]
    condition_data['Resistances'] = window['_ResistanceModList_'].get_list_values()
    condition_data['Action Modifier'] = values['_ACTIONMOD_']
    condition_data['Bonus Action Modifier'] = values['_BONUSACTIONMOD_']
    condition_data['Reaction Modifier'] = values['_REACTIONMOD_']
    condition_data['Damage Over Time Roll'] = values['_DAMAGEOVERTIMEROLL_']
    condition_data['Damage Over Time Type'] = values['_DAMAGEOVERTIMETYPE_']
    condition_data['Healing Over Time'] = values['_HEALINGOVERTIMEROLL_']
    condition_data['Paired Condition'] = values['_PAIREDCONDITION_']



#Condition Events
def events(event,values,window):
    global condition_data

    if event == '_CONDITIONS_' and len(values['_CONDITIONS_']):
        selected_condition = values['_CONDITIONS_']
        selected_condition_name = selected_condition[0]
        filename = os.path.join(os.getcwd(), 'Conditions', f'{selected_condition_name}.json')
        print(filename)
        if os.path.exists(filename):
            condition_data = load(filename)
        else:
            condition_data = base_condition_data
        update_condition(condition_data,window)
    
    elif event == 'Create New Condition':
        condition_data = copy.deepcopy(base_condition_data)
        update_condition(condition_data,window)
    
    elif event == 'Add Resistance/Vulnerability/Immunity Modifier':
        resistance_data = window['_ResistanceModList_'].get_list_values()
        resistance_data.append([values['_DAMAGETYPERESISTANCEMOD_'], values['_RESISTANCETYPEMOD_']])
        window['_ResistanceModList_'].update(resistance_data)
    elif event == 'Delete Resistance/Vulnerability/Immunity Modifier' and values['_ResistanceModList_']:
        selected_resistance = values['_ResistanceModList_'][0]
        resistance_data = window['_ResistanceModList_'].get_list_values()
        resistance_data.remove(selected_resistance)
        window['_ResistanceModList_'].update(resistance_data)
        condition_data['Resistances'] = window['_ResistanceModList_'].get_list_values()
    
    elif event == 'Add Damage Over Time':
        damage_roll = values['_DAMAGEOVERTIMEROLL_']
        damage_type = values['_DAMAGEOVERTIMETYPE_']
        damage_data = window['_DamageOverTimeList_'].get_list_values()
        damage_data.append({'Damage Roll': damage_roll, 'Damage Type': damage_type})
        window['_DamageOverTimeList_'].update(damage_data)
    elif event == 'Remove Damage Over Time' and values['_DamageOverTimeList_']:
        selected_damage = values['_DamageOverTimeList_'][0]
        damage_data = window['_DamageOverTimeList_'].get_list_values()
        damage_data.remove(selected_damage)
        window['_DamageOverTimeList_'].update(damage_data)
    
    elif event == 'Save Condition':# Update condition_data with input values
        update_condition_data(values,window)

        # Show a file save dialog and get the chosen filename
        #filename = sg.popup_get_file('Save Condition Data', save_as=True, default_extension='.json', file_types=(('JSON Files', '*.json'),))
        filename = os.path.join(os.getcwd(),'Conditions')
        filename = os.path.join(filename,f"{condition_data['Name']}.json")
        
        if filename:
            save(filename, condition_data)
            sg.popup(f'Condition data saved to {filename}', title='Save Successful')
            window.Element('_CONDITIONS_').Update(get_conditions_list())
    elif event == 'Load Condition':
        # Show a file open dialog and get the chosen filename
        #filename = sg.popup_get_file('Load Condition Data', file_types=(('JSON Files', '*.json'),))
        filename = os.path.join(os.getcwd(),'Conditions')
        filename = os.path.join(filename,f"{condition_data['Name']}.json")
        
        if filename:
            condition_data = load(filename)
            update_condition(condition_data,window)
            sg.popup(f'Condition data loaded from {filename}', title='Load Successful')
    
    elif values['_INPUTCONDITION_'] != '':
        search = values['_INPUTCONDITION_']
        new_values = [x for x in get_conditions_list() if search.lower() in x.lower()]
        window.Element('_CONDITIONS_').Update(new_values)
        
    else:
        window.Element('_CONDITIONS_').Update(get_conditions_list())