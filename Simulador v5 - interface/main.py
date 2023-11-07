import PySimpleGUI as sg
import json
import os
import re
from simulator import Simulator
from creature import Creature
from action import Action, Attack_Roll, Auto_Apply, Saving_Throw, Damage, Healing, Apply_Condition
from conditions import Condition, Condition_Effect, Modified_Attack, Modified_Defense, Modified_Economy

sg.theme('SystemDefaultForReal')
ttk_style = 'vista'
simulator = Simulator()

#Function to format creatures from the interface to the simulator
def format_creature(creature):
    actionlist = []
    for action in creature['Actions']:
        if action['Effect'] == 'Damage':
            damage_roll = re.split('[d\+]', action['Damage Roll'])
            effect = Damage(int(damage_roll[0]), int(damage_roll[1]), int(damage_roll[2]), action['Damage Type'])
        if action['Action Type'] == 'Attack Roll':
            attempt = Attack_Roll(int(action['Attack Bonus']), effect)
        resourcecost = None
        for resource in action['Resource Cost']:
            resourcecost = [resource['Name'], int(resource['Number'])]
        formatted_action = Action(action['Name'], int(action['Number of Targets']), action['Target Type'], attempt, resourcecost)
        actionlist.append(formatted_action)
    formatted_creature = Creature(creature['Name'], int(creature['HP']), int(creature['AC']), list(map(int, creature['Saving Throws'])), int(creature['Iniciative']))
    for resource in creature['Resources']:
        formatted_creature.add_resource(resource['Name'], int(resource['Number']), resource['Type'])
    for formatted_action in actionlist:
        formatted_creature.add_action(formatted_action)
    #Add combos here later
    for formatted_action in actionlist:
        formatted_creature.add_combo([formatted_action.name])
    return formatted_creature

#Function to run the simulations
def run_simulation(team1, team2, iterations):
    #Formatting creatures
    formatted_team1 = []
    formatted_team2 = []
    for creature in team1:
        formatted_team1.append(format_creature(creature))
    for creature in team2:
        formatted_team2.append(format_creature(creature))
    simulator.start_simulation(formatted_team1,formatted_team2)

# Function to save to file
def save(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)
    
def load(filename):
    with open(filename, 'r') as file:
        return json.load(file)
        


# Function to save creature data to a file
def save_creature(filename):
    with open(filename, 'w') as file:
        json.dump(creature_data, file)

# Function to load creature data from a file
def load_creature(filename):
    with open(filename, 'r') as file:
        return json.load(file)

#Function to get the names of all creatures in the "Creatures" folder.        
def get_creatures_list():
    creatures_folder = os.path.join(os.getcwd(), 'Creatures')
    if not os.path.exists(creatures_folder):
        os.makedirs(creatures_folder)

    creatures = []
    for file in os.listdir(creatures_folder):
        if file.endswith('.json'):
            creatures.append(file[:-5])  # Remove .json extension
    return creatures

# Function to save condition data to a file
def save_condition(filename):
    with open(filename, 'w') as file:
        json.dump(condition_data, file)

# Function to load condition data from a file
def load_condition(filename):
    with open(filename, 'r') as file:
        return json.load(file)
    
#Function to get the names of all conditions in the "Conditions" folder.        
def get_conditions_list():
    conditions_folder = os.path.join(os.getcwd(), 'Conditions')
    if not os.path.exists(conditions_folder):
        os.makedirs(conditions_folder)

    conditions = []
    for file in os.listdir(conditions_folder):
        if file.endswith('.json'):
            conditions.append(file[:-5])  # Remove .json extension
    return conditions

# Function to save action data to a file
def save_action(filename):
    with open(filename, 'w') as file:
        json.dump(action_data, file)

# Function to load action data from a file
def load_action(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Function to get the names of all actions in the "Actions" folder
def get_actions_list():
    actions_folder = os.path.join(os.getcwd(), 'Actions')
    if not os.path.exists(actions_folder):
        os.makedirs(actions_folder)

    actions = []
    for file in os.listdir(actions_folder):
        if file.endswith('.json'):
            actions.append(file[:-5])  # Remove .json extension
    return actions


# Define layouts for different views
layout_creature_stats = [
    [sg.Text("Name", size=(4, 1)), sg.Input(size=(50, 1), key='_CREATURENAME_', justification='left', enable_events=True)],
    [sg.Text("HP", size=(2, 1)), sg.Input(size=(5, 1), key='_HP_', justification='left', enable_events=True),
    sg.Text("AC", size=(2, 1)), sg.DropDown(values=[str(i) for i in range(31)], size=(5, 1), key='_AC_'),
    sg.Text("Iniciative", size=(10, 1)), sg.DropDown(values=[str(i) for i in range(5, 31)], size=(5, 1), key='_INICIATIVE_')],
    [sg.Text("Saving Throws")],
    [sg.Text("STR", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(5, 31)], size=(3, 1), key='_ST1_'),
    sg.Text("DEX", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(5, 31)], size=(3, 1), key='_ST2_'),
    sg.Text("CON", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(5, 31)], size=(3, 1), key='_ST3_'),
    sg.Text("INT", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(5, 31)], size=(3, 1), key='_ST4_'),
    sg.Text("WIS", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(5, 31)], size=(3, 1), key='_ST5_'),
    sg.Text("CHA", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(5, 31)], size=(3, 1), key='_ST6_')],
    [sg.Text("Resources")],
    [sg.Text("Name", size=(4, 1)), sg.Input(size=(20, 1), key='_ResourceName_'), 
    sg.Text("Number", size=(6, 1)), sg.Input(size=(5, 1), key='_ResourceNumber_'),
    sg.Text("Type", size=(4, 1)), sg.Combo(['Short Rest', 'Long Rest', 'Start of Turn', 'Recharge X'], size=(15, 1), key='_ResourceType_')],
    [sg.Button('Add Resource', use_ttk_buttons=True)],
    [sg.Listbox(values=[], size=(50, 5), key='_ResourcesList_')],
    [sg.Text("Actions")],
    [sg.Button('Add Action', use_ttk_buttons=True)],
    [sg.Listbox(values=[], size=(50, 5), key='_ActionList_')],
    [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Creature'),
    sg.Button('Load', size=(10, 1), use_ttk_buttons=True, key='Load Creature')]
]

layout_creatures_sidebar = [
    [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTCREATURE_', enable_events=True)],
    [sg.Listbox(values=get_creatures_list(), size=(20, 30), key='_CREATURES_', enable_events=True)],
    [sg.Button('Add', use_ttk_buttons=True, key='Create New Creature')]
]

layout_creatures = [
    [sg.Column(layout_creatures_sidebar, element_justification='c'), sg.VerticalSeparator(), sg.Column(layout_creature_stats)]
]

layout_conditions_stats = [
    [sg.Text("Name", size=(4, 1)), sg.Input(size=(50, 1), key='_CONDITIONNAME_', justification='left', enable_events=True)],
    [sg.Text("Duration", size=(8,1)), sg.DropDown(values=[str(i) for i in range(1, 11)], size=(5,1), key='_DURATION_'), 
    sg.Text('Turns, ends on', size=(14,1)), sg.DropDown(values=['start of','end of'], size=(8,1), key='_ENDTYPE_'), 
    sg.DropDown(values=['caster turn','target turn'], size=(11,1), key='_ENDON_')],
    [sg.Text("Attack modifier", size=(15,1)), sg.Input(size=(3,1), key='_ATTACKMOD_'), 
    sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ATTACKADVANTAGE_'),
    sg.Text("Damage modifier", size=(15,1)), sg.Input(size=(3,1), key='_DAMAGEMOD_')],
    [sg.Text("AC modifier", size=(11,1)), sg.Input(size=(3,1), key='_ACMOD_'),
    sg.Text("Attacks against made at", size=(23,1)), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_DEFENSEADVANTAGE_')],
    [sg.Text("Saving Throw Modifiers", size=(21,1))],
    [sg.Text("STR", size=(3,1)), sg.Input(size=(3,1), key='_ST1MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST1ADVANTAGE_')],
    [sg.Text("DEX", size=(3,1)), sg.Input(size=(3,1), key='_ST2MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST2ADVANTAGE_')],
    [sg.Text("CON", size=(3,1)), sg.Input(size=(3,1), key='_ST3MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST3ADVANTAGE_')],
    [sg.Text("INT", size=(3,1)), sg.Input(size=(3,1), key='_ST4MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST4ADVANTAGE_')],
    [sg.Text("WIS", size=(3,1)), sg.Input(size=(3,1), key='_ST5MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST5ADVANTAGE_')],
    [sg.Text("CHA", size=(3,1)), sg.Input(size=(3,1), key='_ST6MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST6ADVANTAGE_')],
    [sg.Text("Amount modifiers",size=(16,1))],
    [sg.Text("Actions",size=(7,1)), sg.Input(size=(3,1), key='_ACTIONMOD_'),
    sg.Text("Bonus actions",size=(13,1)), sg.Input(size=(3,1), key='_BONUSACTIONMOD_'),
    sg.Text("Reactions",size=(9,1)), sg.Input(size=(3,1), key='_REACTIONMOD_')],
    [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Condition'),
    sg.Button('Load', size=(10, 1), use_ttk_buttons=True, key='Load Condition')]
]

layout_conditions_sidebar = [
    [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTCONDITION_', enable_events=True)],
    [sg.Listbox(values=get_conditions_list(), size=(20, 30), key='_CONDITIONS_', enable_events=True)],
    [sg.Button('Add', use_ttk_buttons=True, key='Create New Condition')]
]

layout_conditions = [
    [sg.Column(layout_conditions_sidebar, element_justification='c'), sg.VerticalSeparator(), sg.Column(layout_conditions_stats)]
]
    
    
layout_action_stats = [
    [sg.Text("Name", size=(8, 1)), sg.Input(size=(50, 1), key='_ACTIONNAME_', justification='left', enable_events=True)],
    [sg.Text("Number of Targets", size=(16, 1)), sg.Input(size=(2, 1), key='_NUMTARGETS_', justification='left', enable_events=True),
    sg.Text("Target Type", size=(11, 1)), sg.Combo(['Self', 'Enemy', 'Ally'], size=(6, 1), key='_TARGETTYPE_')],
    [sg.Text("Action Type", size=(8, 1)), sg.Combo(['Attack Roll', 'Saving Throw', 'Auto Apply'], size=(12, 1), key='_ACTIONTYPE_', enable_events=True)],
    [sg.Text("Effect", size=(8, 1)), sg.Combo(['Damage', 'Healing', 'Apply Condition'], size=(12, 1), key='_EFFECT_', enable_events=True)],
    [sg.Text("Properties")],
    [sg.Text("Attack Bonus", size=(12, 1)), sg.Input(size=(2, 1), key='_ATTACKBONUS_', justification='left', enable_events=True, visible=False)],
    [sg.Text("Save DC", size=(8, 1)), sg.Input(size=(2, 1), key='_SAVEDC_', justification='left', enable_events=True, visible=False)],
    [sg.Text("Save Type", size=(8, 1)), sg.Combo(['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'], size=(5, 1), key='_SAVETYPE_', visible=False)],
    [sg.Text("Damage (XdY+Z)", size=(13, 1)), sg.Input(size=(10, 1), key='_DAMAGEROLL_', justification='left', enable_events=True, visible=False)],
    [sg.Text("Damage Type", size=(11, 1)), sg.Input(size=(15, 1), key='_DAMAGETYPE_', justification='left', enable_events=True, visible=False)],
    [sg.Text("Resource Name", size=(16, 1)), sg.Input(size=(20, 1), key='_ACTIONRESOURCENAME_', justification='left', enable_events=True),
    sg.Text("Resource Cost", size=(16, 1)), sg.Input(size=(5, 1), key='_ACTIONRESOURCECOST_', justification='left', enable_events=True)],
    [sg.Button('Add Cost', use_ttk_buttons=True)],
    [sg.Listbox(values=[], size=(50, 5), key='_ResourceCosts_')],
    [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Action'),
    sg.Button('Load', size=(10, 1), use_ttk_buttons=True, key='Load Action')]
]

layout_actions_sidebar = [
    [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTACTION_', enable_events=True)],
    [sg.Listbox(values=get_actions_list(), size=(20, 30), key='_ACTIONS_', enable_events=True)],
    [sg.Button('Add', use_ttk_buttons=True, key='Create New Action')]
]

layout_actions = [
    [sg.Column(layout_actions_sidebar, element_justification='c'), sg.VerticalSeparator(), sg.Column(layout_action_stats)]
]


layout_simulator = [
    [sg.Button('Add Creature to Team 1', use_ttk_buttons=True, key='Add Creature 1'), sg.Button('Add Creature to Team 2', use_ttk_buttons=True, key='Add Creature 2')],
    [sg.Listbox(values=[], size=(20, 30), key='_TEAM1_', enable_events=True), sg.Listbox(values=[], size=(20, 30), key='_TEAM2_', enable_events=True)],
    [sg.Button('Simulate', use_ttk_buttons=True, key='Simulate')]
]

# Create the main window layout with the menu
layout_main = [
    [sg.Menu([['Menu', ['Creature','Action', 'Condition', 'Simulator']]])],  # Corrected menu definition
    [sg.Column(layout_creatures, key='_CREATURE_', visible=True),
     sg.Column(layout_actions, key='_ACTION_', visible=False),
     sg.Column(layout_conditions, key='_CONDITION_', visible=False),
     sg.Column(layout_simulator, key='_SIMULATOR_', visible=False)]
]

window = sg.Window('Menu Example', layout_main, ttk_theme=ttk_style, size=(800, 600))  # Adjusted window size

base_creature_data = {
    'Name': 'New Creature',
    'HP': 1,
    'AC': 10,
    'Iniciative': 0,
    'Saving Throws': [0, 0, 0, 0, 0, 0],
    'Resources': [],
    'Actions': []
}

creature_data = {
    'Name': None,
    'HP': None,
    'AC': None,
    'Iniciative': None,
    'Saving Throws': [None, None, None, None, None, None],
    'Resources': [],
    'Actions': []
}

def update_creature(creature_data):
    window['_CREATURENAME_'].update(creature_data['Name'])
    window['_HP_'].update(creature_data['HP'])
    window['_AC_'].update(creature_data['AC'])
    window['_INICIATIVE_'].update(creature_data['Iniciative'])
    for i in range(1, 7):
        window[f'_ST{i}_'].update(creature_data['Saving Throws'][i-1])
    window['_ResourcesList_'].update(creature_data['Resources'])
    window['_ActionList_'].update(creature_data['Actions'])

def update_creature_data(values):
    creature_data['Name'] = values['_CREATURENAME_']
    creature_data['HP'] = values['_HP_']
    creature_data['AC'] = values['_AC_']
    creature_data['Iniciative'] = values['_INICIATIVE_']
    creature_data['Saving Throws'] = [values[f'_ST{i}_'] for i in range(1, 7)]
    creature_data['Resources'] = window['_ResourcesList_'].get_list_values()
    creature_data['Actions'] = window['_ActionList_'].get_list_values()
    
base_condition_data = {
    'Name': 'New Condition',
    'End Type': '',
    'End On': '',
    'Duration': 1,
    'Attack Modifier': 0,
    'Attack Advantage': '',
    'Damage Modifier': 0,
    'AC Modifier': 0,
    'Defense Advantage': '',
    'Saves Modifier': [0,0,0,0,0,0],
    'Saves Advantage': ['','','','','',''],
    'Action Modifier': 0,
    'Bonus Action Modifier': 0,
    'Reaction Modifier': 0
}    

condition_data = {
    'Name': None,
    'End Type': None,
    'End On': None,
    'Duration': None,
    'Attack Modifier': None,
    'Attack Advantage': None,
    'Damage Modifier': None,
    'AC Modifier': None,
    'Defense Advantage': None,
    'Saves Modifier': [None,None,None,None,None,None],
    'Saves Advantage': [None,None,None,None,None,None],
    'Action Modifier': None,
    'Bonus Action Modifier': None,
    'Reaction Modifier': None
}

def update_condition(condition_data):
    window['_CONDITIONNAME_'].update(condition_data['Name'])
    window['_ENDTYPE_'].update(condition_data['End Type'])
    window['_ENDON_'].update(condition_data['End On'])
    window['_DURATION_'].update(condition_data['Duration'])
    window['_ATTACKMOD_'].update(condition_data['Attack Modifier'])
    window['_ATTACKADVANTAGE_'].update(condition_data['Attack Advantage'])
    window['_DAMAGEMOD_'].update(condition_data['Damage Modifier'])
    window['_ACMOD_'].update(condition_data['AC Modifier'])
    window['_DEFENSEADVANTAGE_'].update(condition_data['Defense Advantage'])
    for i in range(1, 7):
        window[f'_ST{i}MOD_'].update(condition_data['Saves Modifier'][i-1])
        window[f'_ST{i}ADVANTAGE_'].update(condition_data['Saves Advantage'][i-1])
    window['_ACTIONMOD_'].update(condition_data['Action Modifier'])
    window['_BONUSACTIONMOD_'].update(condition_data['Bonus Action Modifier'])
    window['_REACTIONMOD_'].update(condition_data['Reaction Modifier'])

def update_condition_data(values):
    condition_data['Name'] = values['_CONDITIONNAME_']
    condition_data['End Type'] = values['_ENDTYPE_']
    condition_data['End On'] = values['_ENDON_']
    condition_data['Duration'] = values['_DURATION_']
    condition_data['Attack Modifier'] = values['_ATTACKMOD_']
    condition_data['Attack Advantage'] = values['_ATTACKADVANTAGE_']
    condition_data['Damage Modifier'] = values['_DAMAGEMOD_']
    condition_data['AC Modifier'] = values['_ACMOD_']
    condition_data['Defense Advantage'] = values['_DEFENSEADVANTAGE_']
    condition_data['Saves Modifier'] = [values[f'_ST{i}MOD_'] for i in range(1, 7)]
    condition_data['Saves Advantage'] = [values[f'_ST{i}ADVANTAGE_'] for i in range(1, 7)]
    condition_data['Action Modifier'] = values['_ACTIONMOD_']
    condition_data['Bonus Action Modifier'] = values['_BONUSACTIONMOD_']
    condition_data['Reaction Modifier'] = values['_REACTIONMOD_']

base_action_data = {
    'Name': 'New Action',
    'Number of Targets': 1,
    'Target Type': 'Self',
    'Resource Cost': [],
    'Action Type': 'Attack Roll',
    'Effect': 'Damage',
    'Attack Bonus': 0,
    'Save DC': 10,
    'Save Type': 'STR',
    'Damage Roll': '1d6+0',
    'Damage Type': 'Bludgeoning'
}

action_data = {
    'Name': None,
    'Number of Targets': None,
    'Target Type': None,
    'Resource Cost': [],
    'Action Type': None,
    'Effect': None,
    'Attack Bonus': None,
    'Save DC': None,
    'Save Type': None,
    'Damage Roll': None,
    'Damage Type': None
}

def update_action(action_data):
    window['_ACTIONNAME_'].update(action_data['Name'])
    window['_NUMTARGETS_'].update(action_data['Number of Targets'])
    window['_TARGETTYPE_'].update(action_data['Target Type'])
    window['_ResourceCosts_'].update(action_data['Resource Cost'])
    window['_ACTIONTYPE_'].update(action_data['Action Type'])
    window['_EFFECT_'].update(action_data['Effect'])
    window['_ATTACKBONUS_'].update(action_data['Attack Bonus'])
    window['_SAVEDC_'].update(action_data['Save DC'])
    window['_SAVETYPE_'].update(action_data['Save Type'])
    window['_DAMAGEROLL_'].update(action_data['Damage Roll'])
    window['_DAMAGETYPE_'].update(action_data['Damage Type'])

def update_action_data(values):
    action_data['Name'] = values['_ACTIONNAME_']
    action_data['Number of Targets'] = values['_NUMTARGETS_']
    action_data['Target Type'] = values['_TARGETTYPE_']
    action_data['Resource Cost'] = window['_ResourceCosts_'].get_list_values()
    action_data['Action Type'] = values['_ACTIONTYPE_']
    action_data['Effect'] = values['_EFFECT_']
    action_data['Attack Bonus'] = values['_ATTACKBONUS_']
    action_data['Save DC'] = values['_SAVEDC_']
    action_data['Save Type'] = values['_SAVETYPE_']
    action_data['Damage Roll'] = values['_DAMAGEROLL_']
    action_data['Damage Type'] = values['_DAMAGETYPE_']

simulation_data = {
    'Team1': [],
    'Team2': [],
    'Repetitions': 1
}


# Event loop
while True:
    event, values = window.read()
    #Closing Event
    if event == sg.WIN_CLOSED:
        break
        
    #Menu Events
    if event == 'Creature':
        window['_CREATURE_'].update(visible=True)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
    elif event == 'Action':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=True)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
    elif event == 'Condition':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=True)
        window['_SIMULATOR_'].update(visible=False)
    elif event == 'Simulator':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=True)
    
    #Creature Events
    elif event == '_CREATURES_' and len(values['_CREATURES_']):
        selected_creature = values['_CREATURES_']
        selected_creature_name = selected_creature[0]
        filename = os.path.join(os.getcwd(), 'Creatures', f'{selected_creature_name}.json')
        if os.path.exists(filename):
            creature_data = load(filename)
        else:
            creature_data = base_creature_data
        update_creature(creature_data)
    elif event == 'Add Resource':
        name = values['_ResourceName_']
        number = values['_ResourceNumber_']
        rtype = values['_ResourceType_']
        resource_data = window['_ResourcesList_'].get_list_values()
        resource_data.append({'Name': name, 'Number': number, 'Type': rtype})
        window['_ResourcesList_'].update(resource_data)
    elif event == 'Add Action':
        filename = sg.popup_get_file('Load Action Data', file_types=(('JSON Files', '*.json'),))
        if filename:
            action_data = load(filename)
            creature_data['Actions'].append(action_data)
            window['_ActionList_'].update(creature_data['Actions'])
    elif event == 'Create New Creature':
        window['_CREATURES_'].update(values=get_creatures_list() + ['New Creature'])
        window['_CREATURES_'].set_value('New Creature')
        creature_data = base_creature_data
        update_creature(creature_data)
    elif event == 'Save Creature':# Update creature_data with input values
        update_creature_data(values)

        # Show a file save dialog and get the chosen filename
        filename = sg.popup_get_file('Save Creature Data', save_as=True, default_extension='.json', file_types=(('JSON Files', '*.json'),))
        
        if filename:
            save(filename, creature_data)
            sg.popup(f'Creature data saved to {filename}', title='Save Successful')         
    elif event == 'Load Creature':
        # Show a file open dialog and get the chosen filename
        filename = sg.popup_get_file('Load Creature Data', file_types=(('JSON Files', '*.json'),))
        
        if filename:
            creature_data = load(filename)
            update_creature(creature_data)
            sg.popup(f'Creature data loaded from {filename}', title='Load Successful')
    
    
    #Condition Events
    elif event == '_CONDITIONS_' and len(values['_CONDITIONS_']):
        selected_condition = values['_CONDITIONS_']
        selected_condition_name = selected_condition[0]
        filename = os.path.join(os.getcwd(), 'Conditions', f'{selected_condition_name}.json')
        print(filename)
        if os.path.exists(filename):
            condition_data = load(filename)
        else:
            condition_data = base_condition_data
        update_condition(condition_data)
    elif event == 'Create New Condition':
        window['_CONDITIONS_'].update(values=get_conditions_list() + ['New Condition'])
        window['_CONDITIONS_'].set_value('New Condition')
        condition_data = base_condition_data
        update_condition(condition_data)
    elif event == 'Save Condition':# Update condition_data with input values
        update_condition_data(values)

        # Show a file save dialog and get the chosen filename
        filename = sg.popup_get_file('Save Condition Data', save_as=True, default_extension='.json', file_types=(('JSON Files', '*.json'),))
        
        if filename:
            save(filename, condition_data)
            sg.popup(f'Condition data saved to {filename}', title='Save Successful')         
    elif event == 'Load Condition':
        # Show a file open dialog and get the chosen filename
        filename = sg.popup_get_file('Load Condition Data', file_types=(('JSON Files', '*.json'),))
        
        if filename:
            condition_data = load(filename)
            update_condition(condition_data)
            sg.popup(f'Condition data loaded from {filename}', title='Load Successful')
    
    #Action Events
    elif event == '_ACTIONS_' and len(values['_ACTIONS_']):
        selected_action = values['_ACTIONS_']
        selected_action_name = selected_action[0]
        filename = os.path.join(os.getcwd(), 'Actions', f'{selected_action_name}.json')
        print(filename)
        if os.path.exists(filename):
            action_data = load(filename)
        else:
            action_data = base_action_data
        update_action(action_data)
        window['_ATTACKBONUS_'].update(visible=action_data['Action Type'] == 'Attack Roll')
        window['_SAVEDC_'].update(visible=action_data['Action Type'] == 'Saving Throw')
        window['_SAVETYPE_'].update(visible=action_data['Action Type'] == 'Saving Throw')
        window['_DAMAGEROLL_'].update(visible=action_data['Effect'] == 'Damage')
        window['_DAMAGETYPE_'].update(visible=action_data['Effect'] == 'Damage')
    elif event == '_ACTIONTYPE_':
        window['_ATTACKBONUS_'].update(visible=values['_ACTIONTYPE_'] == 'Attack Roll')
        window['_SAVEDC_'].update(visible=values['_ACTIONTYPE_'] == 'Saving Throw')
        window['_SAVETYPE_'].update(visible=values['_ACTIONTYPE_'] == 'Saving Throw')
    elif event == '_EFFECT_':
        window['_DAMAGEROLL_'].update(visible=values['_EFFECT_'] == 'Damage')
        window['_DAMAGETYPE_'].update(visible=values['_EFFECT_'] == 'Damage')
    elif event == 'Add Cost':
        name = values['_ACTIONRESOURCENAME_']
        number = values['_ACTIONRESOURCECOST_']
        resource_data = window['_ResourceCosts_'].get_list_values()
        resource_data.append({'Name': name, 'Number': number})
        window['_ResourceCosts_'].update(resource_data)
    elif event == 'Create New Action':
        window['_ACTIONS_'].update(values=get_actions_list() + ['New Action'])
        window['_ACTIONS_'].set_value('New Action')
        action_data = base_action_data
        update_action(action_data)
    elif event == 'Save Action':
        print(values)
        update_action_data(values)

        filename = sg.popup_get_file('Save Action Data', save_as=True, default_extension='.json', file_types=(('JSON Files', '*.json'),))
        
        if filename:
            save(filename, action_data)
            sg.popup(f'Action data saved to {filename}', title='Save Successful')         
    elif event == 'Load Action':
        filename = sg.popup_get_file('Load Action Data', file_types=(('JSON Files', '*.json'),))
        
        if filename:
            action_data = load(filename)
            update_action(action_data)
            sg.popup(f'Action data loaded from {filename}', title='Load Successful')
    
    #Simulator Events
    elif event == 'Add Creature 1':
        filename = sg.popup_get_file('Load Creature Data', file_types=(('JSON Files', '*.json'),))
        if filename:
            creature_data = load(filename)
            simulation_data['Team1'].append(creature_data)
            window['_TEAM1_'].update(simulation_data['Team1'])
    elif event == 'Add Creature 2':
        filename = sg.popup_get_file('Load Creature Data', file_types=(('JSON Files', '*.json'),))
        if filename:
            creature_data = load(filename)
            simulation_data['Team2'].append(creature_data)
            window['_TEAM2_'].update(simulation_data['Team2'])
    elif event == 'Simulate':
        run_simulation(simulation_data['Team1'], simulation_data['Team2'], simulation_data['Repetitions'])
    
    #Search Events
    elif values['_INPUTCREATURE_'] != '' or values['_INPUTCONDITION_'] != '' or values['_INPUTACTION_'] != '' :
        search = values['_INPUTCREATURE_']
        new_values = [x for x in get_creatures_list() if search.lower() in x.lower()]
        window.Element('_CREATURES_').Update(new_values)
        search = values['_INPUTCONDITION_']
        new_values = [x for x in get_conditions_list() if search.lower() in x.lower()]
        window.Element('_CONDITIONS_').Update(new_values)
        search = values['_INPUTACTION_']
        new_values = [x for x in get_actions_list() if search.lower() in x.lower()]
        window.Element('_ACTIONS_').Update(new_values)
    else:
        window.Element('_CREATURES_').Update(get_creatures_list())
        window.Element('_CONDITIONS_').Update(get_conditions_list())
        window.Element('_ACTIONS_').Update(get_actions_list())
        
window.close()