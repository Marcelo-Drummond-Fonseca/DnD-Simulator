import PySimpleGUI as sg
import os
import json

sg.theme('SystemDefaultForReal')
ttk_style = 'xpnative'

damage_types = ['Acid', 'Bludgeoning', 'Bludgeoning (Magical)', 'Cold', 'Fire', 'Force', 'Lightning', 'Necrotic', 'Piercing', 'Piercing (Magical)', 'Poison', 'Psychic', 'Radiant', 'Slashing', 'Slashing (Magical)', 'Thunder']
damage_multiplier = {'Resistance': 0.5, 'Immunity': 0, 'Vulnerability': 2}
saves_dict = {
    'STR': 0,
    'DEX': 1,
    'CON': 2,
    'INT': 3,
    'WIS': 4,
    'CHA': 5
}
condition_end_possibilities = ['Start of Caster Turn',
'End of Caster Turn',
'Start of Target Turn',
'End of Target Turn',
'On Damage Taken',
'Repeat Save on End of Target Turn',
'Repeat Save on Damage Taken']

# Function to save to file
def save(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)

#Function to load from file
def load(filename):
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