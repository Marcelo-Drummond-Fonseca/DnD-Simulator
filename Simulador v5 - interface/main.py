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

damage_types = ['Acid', 'Bludgeoning', 'Bludgeoning (Magical)', 'Cold', 'Fire', 'Force', 'Lightning', 'Necrotic', 'Piercing', 'Piercing (Magical)', 'Poison', 'Psychic', 'Radiant', 'Slashing', 'Slashing (Magical)', 'Thunder']
damage_multiplier = {'Resistance': 0.5, 'Immunity': 0, 'Vulnerability': 2}

opened_creature_action = None

#Function to format conditions from the interface to the simulator.
def format_condition(condition):
    effectslist = []
    print(condition['Name'])
    if condition['Attack Modifier'] or condition['Attack Advantage'] or condition['Damage Modifier']:
        if condition['Attack Advantage'] == 'Advantage': advantage = 1
        elif condition['Attack Advantage'] == 'Disadvantage': advantage = -1
        else: advantage = 0
        effectslist.append(Modified_Attack(int(condition['Attack Modifier']), int(condition['Damage Modifier']), advantage))
    if condition['AC Modifier'] or condition['Defense Advantage'] or condition['Saves Modifier'] or condition['Saves Advantage'] or condition['Resistances']:
        if condition['Defense Advantage'] == 'Advantage': advantage = 1
        elif condition['Defense Advantage'] == 'Disadvantage': advantage = -1
        else: advantage = 0
        resistances = {}
        for resistance in condition['Resistances']:
            resistances[resistance[0]] = damage_multiplier[resistance[1]]
        effectslist.append(Modified_Defense(int(condition['AC Modifier']), advantage, list(map(int, condition['Saves Modifier'])), condition['Saves Advantage'], resistances))
    if condition['Action Modifier'] or condition['Bonus Action Modifier'] or condition['Reaction Modifier']:
        effectslist.append(Modified_Economy(int(condition['Action Modifier']), int(condition['Bonus Action Modifier']), int(condition['Reaction Modifier'])))
    return Condition(condition['Name'], condition['End Type'] + ' ' + condition['End On'], int(condition['Duration']), effectslist)
        
def format_action(action):
    if action['Effect'] == 'Damage':
        total_damage = []
        for damage in action['Damage']:
            damage_formatted = list(map(int,re.split('[d\+]', damage['Damage Roll'])))
            damage_formatted.append(damage['Damage Type'])
            total_damage.append(damage_formatted)
        effect = Damage(total_damage)
    elif action['Effect'] == 'Healing':
        healing_roll = re.split('[d\+]', action['Healing Roll'])
        effect = Healing(int(healing_roll[0]), int(healing_roll[1]), int(healing_roll[2]))
    elif action['Effect'] == 'Apply Condition':
        for condition in action['Conditions']:
            formatted_condition = format_condition(condition)
            effect = Apply_Condition(formatted_condition)
    if action['Action Type'] == 'Attack Roll':
        attempt = Attack_Roll(int(action['Attack Bonus']), effect)
    elif action['Action Type'] == 'Saving Throw':
        attempt = Saving_Throw(int(action['Save DC']), action['Save Type'], True, effect)
    elif action['Action Type'] == 'Auto Apply':
        attempt = Auto_Apply(effect)
    resourcecost = None
    for resource in action['Resource Cost']:
        resourcecost = [resource['Name'], int(resource['Number'])]
    return Action(action['Name'], int(action['Number of Targets']), action['Target Type'], attempt, resourcecost)

#Function to format creatures from the interface to the simulator
def format_creature(creature):
    actionlist = []
    bonusactionlist = []
    freeactionlist = []
    for action in creature['Actions']:
        formatted_action = format_action(action)
        if action['Action Speed'] == 'Action':
            actionlist.append(formatted_action)
        elif action['Action Speed'] == 'Bonus Action':
            bonusactionlist.append(formatted_action)
        elif action['Action Speed'] == 'Free Action':
            freeactionlist.append(formatted_action)
    formatted_creature = Creature(creature['Name'], int(creature['HP']), int(creature['AC']), list(map(int, creature['Saving Throws'])), int(creature['Iniciative']), creature['AI'], creature['Tags'])
    for resource in creature['Resources']:
        formatted_creature.add_resource(resource['Name'], int(resource['Number']), resource['Type'])
    for formatted_action in actionlist:
        formatted_creature.add_action(formatted_action)
    for formatted_action in bonusactionlist:
        formatted_creature.add_bonus_action(formatted_action)
    for formatted_action in freeactionlist:
        formatted_creature.add_free_action(formatted_action)
    #Add combos here later
    if creature['Combos']:
        for combo in creature['Combos']:
            formatted_creature.add_combo(combo.split(','))
    else:
        for formatted_action in actionlist:
            formatted_creature.add_combo([formatted_action.name])
    for resistance in creature['Resistances']:
        formatted_creature.add_damage_type_multiplier(resistance[0],damage_multiplier[resistance[1]])
    return formatted_creature

#Function to run the simulations
def run_simulation(team1, team2, iterations):
    #Formatting creatures
    formatted_team1 = []
    formatted_team2 = []
    winrate1 = 0
    winrate2 = 0
    deaths_total = {}
    uncertainty_total = 0
    duration_total = 0
    permanency_team1 = 0
    permanency_team2 = 0
    
    for creature in team1:
        formatted_team1.append(format_creature(creature))
    for creature in team2:
        formatted_team2.append(format_creature(creature))
    for i in range(iterations):
        for creature in formatted_team1:
            creature.full_restore()
        for creature in formatted_team2:
            creature.full_restore()
        response = simulator.start_simulation(formatted_team1.copy(),formatted_team2.copy())
        
        
        #Calculando métricas
        scores = response['scores']
        advantage_record = response['advantage_record']
        deaths = response['deaths']
        rounds = response['rounds']
        
        for death in deaths:
            if death in deaths_total:
                deaths_total[death] += 1/iterations
            else:
                deaths_total[death] = 1/iterations
                
        print(f'deaths: {deaths}')
        
        #Incerteza
        uncertainty = 0
        for i in range(1, len(advantage_record)):
            if advantage_record[i] != advantage_record[i - 1]:
                uncertainty += 1
        uncertainty = uncertainty/rounds
        print(f'Incerteza: {uncertainty}')
        uncertainty_total += uncertainty
        
        #Duração
        duration_total += rounds
        print(f'Duração: {rounds} rounds')
        
        #Permanencia
        leader_rounds = 1
        permanency_amount = 1
        leader_id = lst[0]
        permanency_leader = leader_id

        for i in range(1, len(lst)):
            if lst[i] == lst[i - 1]:
                leader_rounds += 1
            else:
                if leader_rounds > permanency_amount:
                    permanency_amount = leader_rounds
                    permanency_leader = leader_id

                leader_rounds = 1
                leader_id = lst[i]

        # Check for the last sequence
        if leader_rounds > permanency_amount:
            permanency_amount = leader_rounds
            permanency_leader = leader_id
        if permanency_leader == 1:
            permanency_team1 += permanency_amount
        elif permanency_leader == 2:
            permanency_team2 += permanency_amount
        print(f'A maior permanência foi de {permanency_amount} rounds pelo time {permanency_leader}')
        
        
        #Desafio
        winner = response['winner']
        if winner == 1:
            winrate1 += 1
        elif winner == 2:
            winrate2 += 1    
    
    print('Team 1 winrate: ' + str(round(winrate1*100/iterations,2)) + '%\nTeam 2 winrate: ' + str(round(winrate2*100/iterations,2)) + '%')
    print(f'Duração média: {duration_total/iterations}')
    print(f'mortes (em média): {deaths_total}')
    print(f'Incerteza média: {uncertainty_total/iterations}')
    print(f'Permanencia média do time 1: {permanency_team1/iterations}')
    print(f'Permanencia média do time 2: {permanency_team2/iterations}')
    return 'Team 1 winrate: ' + str(round(winrate1*100/iterations,2)) + '%\nTeam 2 winrate: ' + str(round(winrate2*100/iterations,2)) + '%'
    

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


# Define layouts for different views

layout_creature_statistics =[
    [sg.Text("Name", size=(4, 1)), sg.Input(size=(50, 1), key='_CREATURENAME_', justification='left', enable_events=True)],
    [sg.Text("HP", size=(2, 1)), sg.Input(size=(5, 1), key='_HP_', justification='left', enable_events=True),
    sg.Text("AC", size=(2, 1)), sg.DropDown(values=[str(i) for i in range(5,31)], size=(5, 1), key='_AC_'),
    sg.Text("Iniciative", size=(10, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(5, 1), key='_INICIATIVE_')],
    [sg.Text("AI", size=(2,1)), sg.DropDown(values=['Melee','Ranged','Support'], size=(7,1), key='_AI_')],
    [sg.Text("Saving Throws")],
    [sg.Text("STR", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST1_'),
    sg.Text("DEX", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST2_'),
    sg.Text("CON", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST3_'),
    sg.Text("INT", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST4_'),
    sg.Text("WIS", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST5_'),
    sg.Text("CHA", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST6_')],
    [sg.Text("Resistances/Immunities/Vulnerabilities")],
    [sg.DropDown(values=damage_types, key='_DAMAGETYPERESISTANCE_'), sg.Combo(values=['Resistance','Immunity','Vulnerability'], key='_RESISTANCETYPE_')],
    [sg.Button('Add Resistance/Vulnerability/Immunity', use_ttk_buttons=True), sg.Button('Delete Resistance/Vulnerability/Immunity', use_ttk_buttons=True)],
    [sg.Listbox(values=[], size=(50, 5), key='_ResistanceList_')],
    [sg.Text("Tags")],
    [sg.Input(size=(50, 1), key='_CREATURETAG_')],
    [sg.Button('Add Creature Tag', use_ttk_buttons=True), sg.Button('Delete Creature Tag', use_ttk_buttons=True)],
    [sg.Listbox(values=[], size=(50, 5), key='_CreatureTagList_')]
]

layout_creature_resources = [
    [sg.Text("Resources")],
    [sg.Text("Name", size=(4, 1)), sg.Input(size=(20, 1), key='_ResourceName_'), 
    sg.Text("Number", size=(6, 1)), sg.Input(size=(5, 1), key='_ResourceNumber_'),
    sg.Text("Type", size=(4, 1)), sg.Combo(['Short Rest', 'Long Rest', 'Start of Turn', 'Recharge X'], size=(15, 1), key='_ResourceType_')],
    [sg.Button('Add Resource', use_ttk_buttons=True), sg.Button('Delete Resource', use_ttk_buttons=True)],
    [sg.Listbox(values=[], size=(50, 5), key='_ResourcesList_')]
]

layout_creature_combos = [
    [sg.Text("Combos")],
    [sg.Input(size=(30,1), key='_COMBONAME_', justification='left', enable_events=True)],
    [sg.Button('Add Combo', use_ttk_buttons=True), sg.Button('Delete Combo', use_ttk_buttons=True)],
    [sg.Listbox(values=[], size=(50, 5), key='_ComboList_')]

]

layout_creature_actions_editor = [
    [sg.Text("Name", size=(8, 1)), sg.Input(size=(50, 1), key='_CREATUREACTIONNAME_', justification='left', enable_events=True)],
    [sg.Text("Attack Bonus", size=(12, 1)), sg.Input(size=(2, 1), key='_CREATUREACTIONATTACKBONUS_', justification='left', enable_events=True, visible=True)],
    [sg.Text("Save DC", size=(8, 1)), sg.Input(size=(2, 1), key='_CREATUREACTIONSAVEDC_', justification='left', enable_events=True, visible=True)],
    [sg.Text("Save Type", size=(8, 1)), sg.Combo(['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'], size=(5, 1), key='_CREATUREACTIONSAVETYPE_', visible=True)],
    [sg.Text("Damage (XdY+Z)", size=(13, 1)), sg.Input(size=(10, 1), key='_CREATUREACTIONDAMAGEROLL_', justification='left', enable_events=True, visible=True)],
    [sg.Text("Damage Type", size=(11, 1)), sg.Combo(values=damage_types, key='_CREATUREACTIONDAMAGETYPE_', enable_events=True, visible=True)],
    [sg.Button('Add Damage', use_ttk_buttons=True, visible=True, key='_CREATUREACTIONADDDAMAGE_'), sg.Button('Delete Damage', use_ttk_buttons=True, visible=True, key='_CREATUREACTIONDELETEDAMAGE_')],
    [sg.Listbox(values=[], size=(50, 5), key='_CreatureActionDamageList_')],
    [sg.Text("Healing (XdY+Z)", size=(13, 1)), sg.Input(size=(10, 1), key='_CREATUREACTIONHEALINGROLL_', justification='left', enable_events=True, visible=True)],
    [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Creature Action')]
]

layout_creature_actions_sidebar = [
    [sg.Listbox(values=[], size=(20, 30), key='_ActionList_', enable_events=True)],
    [sg.Button('Add Action', use_ttk_buttons=True), sg.Button('Delete Action', use_ttk_buttons=True)]
]



layout_creature_actions = [
    [sg.Column(layout_creature_actions_sidebar, element_justification='c'), sg.VerticalSeparator(), sg.Column(layout_creature_actions_editor)]
]

layout_creature_stats = [
    [sg.Column(layout_creature_statistics, key='_CREATURESTATS_', visible=True),
    sg.Column(layout_creature_actions, key='_CREATUREACTIONS_', visible=False),
    sg.Column(layout_creature_combos, key='_CREATURECOMBOS_', visible=False),
    sg.Column(layout_creature_resources, key='_CREATURERESOURCES_', visible=False)],
    
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

layout_condition_statistics = [
    [sg.Text("Name", size=(4, 1)), sg.Input(size=(50, 1), key='_CONDITIONNAME_', justification='left', enable_events=True)],
    [sg.Text("Duration", size=(8,1)), sg.DropDown(values=[str(i) for i in range(1, 11)], size=(5,1), key='_DURATION_'), 
    sg.Text('Turns, ends on', size=(14,1)), sg.DropDown(values=['Start Of','End Of'], size=(8,1), key='_ENDTYPE_'), 
    sg.DropDown(values=['Caster Turn','Target Turn'], size=(11,1), key='_ENDON_')],
]

layout_condition_offenses = [
    [sg.Text("Attack modifier", size=(15,1)), sg.Input(size=(3,1), key='_ATTACKMOD_'), 
    sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ATTACKADVANTAGE_'),
    sg.Text("Damage modifier", size=(15,1)), sg.Input(size=(3,1), key='_DAMAGEMOD_')]
]

layout_condition_defenses = [
    [sg.Text("AC modifier", size=(11,1)), sg.Input(size=(3,1), key='_ACMOD_'),
    sg.Text("Attacks against made at", size=(23,1)), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_DEFENSEADVANTAGE_')],
    [sg.Text("Saving Throw Modifiers", size=(21,1))],
    [sg.Text("STR", size=(3,1)), sg.Input(size=(3,1), key='_ST1MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST1ADVANTAGE_')],
    [sg.Text("DEX", size=(3,1)), sg.Input(size=(3,1), key='_ST2MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST2ADVANTAGE_')],
    [sg.Text("CON", size=(3,1)), sg.Input(size=(3,1), key='_ST3MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST3ADVANTAGE_')],
    [sg.Text("INT", size=(3,1)), sg.Input(size=(3,1), key='_ST4MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST4ADVANTAGE_')],
    [sg.Text("WIS", size=(3,1)), sg.Input(size=(3,1), key='_ST5MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST5ADVANTAGE_')],
    [sg.Text("CHA", size=(3,1)), sg.Input(size=(3,1), key='_ST6MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST6ADVANTAGE_')],
    [sg.Text("Resistances/Immunities/Vulnerabilities")],
    [sg.DropDown(values=damage_types, key='_DAMAGETYPERESISTANCEMOD_'), sg.Combo(values=['Resistance','Immunity','Vulnerability'], key='_RESISTANCETYPEMOD_')],
    [sg.Button('Add Resistance/Vulnerability/Immunity Modifier', use_ttk_buttons=True), sg.Button('Delete Resistance/Vulnerability/Immunity Modifier', use_ttk_buttons=True)],
    [sg.Listbox(values=[], size=(50, 5), key='_ResistanceModList_')]
]

layout_condition_economy = [
    [sg.Text("Amount modifiers",size=(16,1))],
    [sg.Text("Actions",size=(7,1)), sg.Input(size=(3,1), key='_ACTIONMOD_'),
    sg.Text("Bonus actions",size=(13,1)), sg.Input(size=(3,1), key='_BONUSACTIONMOD_'),
    sg.Text("Reactions",size=(9,1)), sg.Input(size=(3,1), key='_REACTIONMOD_')]
]

layout_conditions_stats = [
    [sg.Column(layout_condition_statistics, key='_CONDITIONSTATS_', visible=True),
    sg.Column(layout_condition_offenses, key='_CONDITIONOFFENSE_', visible=False),
    sg.Column(layout_condition_defenses, key='_CONDITIONDEFENSE_', visible=False),
    sg.Column(layout_condition_economy, key='_CONDITIONECONOMY_', visible=False)],
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
    
    
    
layout_action_statistics = [
    [sg.Text("Name", size=(8, 1)), sg.Input(size=(50, 1), key='_ACTIONNAME_', justification='left', enable_events=True)],
    [sg.Text("Action Speed", size=(12,1)), sg.Combo(['Action', 'Bonus Action', 'Free Action'], size=(12, 1), key='_ACTIONSPEED_')],
    [sg.Text("Number of Targets", size=(16, 1)), sg.Input(size=(2, 1), key='_NUMTARGETS_', justification='left', enable_events=True),
    sg.Text("Target Type", size=(11, 1)), sg.Combo(['Self', 'Enemy', 'Ally'], size=(6, 1), key='_TARGETTYPE_')]
]

layout_action_costs = [
    [sg.Text("Resource Name", size=(16, 1)), sg.Input(size=(20, 1), key='_ACTIONRESOURCENAME_', justification='left', enable_events=True),
    sg.Text("Resource Cost", size=(16, 1)), sg.Input(size=(5, 1), key='_ACTIONRESOURCECOST_', justification='left', enable_events=True)],
    [sg.Button('Add Cost', use_ttk_buttons=True),sg.Button('Delete Cost', use_ttk_buttons=True)],
    [sg.Listbox(values=[], size=(50, 5), key='_ResourceCosts_')]
]

layout_action_effects = [
    [sg.Text("Action Type", size=(8, 1)), sg.Combo(['Attack Roll', 'Saving Throw', 'Auto Apply'], size=(12, 1), key='_ACTIONTYPE_', enable_events=True)],
    [sg.Text("Attack Bonus", size=(12, 1)), sg.Input(size=(2, 1), key='_ATTACKBONUS_', justification='left', enable_events=True, visible=False)],
    [sg.Text("Save DC", size=(8, 1)), sg.Input(size=(2, 1), key='_SAVEDC_', justification='left', enable_events=True, visible=False)],
    [sg.Text("Save Type", size=(8, 1)), sg.Combo(['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'], size=(5, 1), key='_SAVETYPE_', visible=False)],
    [sg.Text("Effect", size=(8, 1)), sg.Combo(['Damage', 'Healing', 'Apply Condition'], size=(12, 1), key='_EFFECT_', enable_events=True)],
    [sg.Text("Damage (XdY+Z)", size=(13, 1)), sg.Input(size=(10, 1), key='_DAMAGEROLL_', justification='left', enable_events=True, visible=False)],
    [sg.Text("Damage Type", size=(11, 1)), sg.Combo(values=damage_types, key='_DAMAGETYPE_', enable_events=True, visible=False)],
    [sg.Button('Add Damage', use_ttk_buttons=True, visible=True, key='_ADDDAMAGE_'), sg.Button('Delete Damage', use_ttk_buttons=True, visible=True, key='_DELETEDAMAGE_')],
    [sg.Listbox(values=[], size=(50, 5), key='_DamageList_')],
    [sg.Text("Healing (XdY+Z)", size=(13, 1)), sg.Input(size=(10, 1), key='_HEALINGROLL_', justification='left', enable_events=True, visible=False)],
    [sg.Button('Add Condition', use_ttk_buttons=True, visible=False, key='_ADDCONDITION_'), sg.Button('Delete Condition', use_ttk_buttons=True, visible=False, key='_DELETECONDITION_')],
    [sg.Listbox(values=[], size=(50, 5), key='_ConditionList_')]
]
    
layout_action_stats = [
    [sg.Column(layout_action_statistics, key='_ACTIONSTATS_', visible=True),
    sg.Column(layout_action_costs, key='_ACTIONCOSTS_', visible=False),
    sg.Column(layout_action_effects, key='_ACTIONEFFECTS_', visible=False)],
    
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
    [sg.Listbox(values=[], size=(20, 20), key='_TEAM1_', enable_events=True), sg.Listbox(values=[], size=(20, 20), key='_TEAM2_', enable_events=True)],
    [sg.Button('Simulate', use_ttk_buttons=True, key='Simulate')],
    [sg.Text("Results:", size=(8,1)), sg.Text('', key='_SIMULATIONRESULTS_')]
]

# Create the main window layout with the menu
layout_main = [
    [sg.Menu([['Creature', ['Creature Stats','Actions', 'Resources', 'Combos']], ['Action',['Action Stats', 'Costs', 'Effects']], ['Condition',['Condition Stats', 'Offense Modifiers','Defense Modifiers', 'Economy Modifiers']], ['Simulator',['Simulator']]])],
    [sg.Column(layout_creatures, key='_CREATURE_', visible=True),
     sg.Column(layout_actions, key='_ACTION_', visible=False),
     sg.Column(layout_conditions, key='_CONDITION_', visible=False),
     sg.Column(layout_simulator, key='_SIMULATOR_', visible=False)]
]

window = sg.Window('Menu Example', layout_main, ttk_theme=ttk_style, size=(800, 1000))  # Adjusted window size

base_creature_data = {
    'Name': 'New Creature',
    'HP': 1,
    'AC': 10,
    'Iniciative': 0,
    'Saving Throws': [0, 0, 0, 0, 0, 0],
    'Resources': [],
    'Actions': [],
    'Combos': [],
    'Resistances': [],
    'AI': 'Melee',
    'Tags': []
}

creature_data = {
    'Name': None,
    'HP': None,
    'AC': None,
    'Iniciative': None,
    'Saving Throws': [None, None, None, None, None, None],
    'Resources': [],
    'Actions': [],
    'Combos': [],
    'Resistances': [],
    'AI': None,
    'Tags': []
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
    window['_ComboList_'].update(creature_data['Combos'])
    window['_ResistanceList_'].update(creature_data['Resistances'])
    if 'AI' in creature_data: window['_AI_'].update(creature_data['AI'])
    if 'Tags' in creature_data: window['_CreatureTagList_'].update(creature_data['Tags'])

def update_creature_data(values):
    creature_data['Name'] = values['_CREATURENAME_']
    creature_data['HP'] = values['_HP_']
    creature_data['AC'] = values['_AC_']
    creature_data['Iniciative'] = values['_INICIATIVE_']
    creature_data['Saving Throws'] = [values[f'_ST{i}_'] for i in range(1, 7)]
    creature_data['Resources'] = window['_ResourcesList_'].get_list_values()
    creature_data['Actions'] = window['_ActionList_'].get_list_values()
    creature_data['Combos'] = window['_ComboList_'].get_list_values()
    creature_data['Resistances'] = window['_ResistanceList_'].get_list_values()
    creature_data['AI'] = values['_AI_']
    creature_data['Tags'] = window['_CreatureTagList_'].get_list_values()
    
def update_creature_action(action):
    window['_CREATUREACTIONNAME_'].update(action['Name'])
    window['_CREATUREACTIONATTACKBONUS_'].update(action['Attack Bonus'])
    window['_CREATUREACTIONSAVEDC_'].update(action['Save DC'])
    window['_CREATUREACTIONSAVETYPE_'].update(action['Save Type'])
    if 'Damage' in action: window['_CreatureActionDamageList_'].update(action['Damage'])
    window['_CREATUREACTIONHEALINGROLL_'].update(action['Healing Roll'])
    
def update_creature_action_data(values):
    opened_creature_action['Name'] = values['_CREATUREACTIONNAME_']
    opened_creature_action['Attack Bonus'] = values['_CREATUREACTIONATTACKBONUS_']
    opened_creature_action['Save DC'] = values['_CREATUREACTIONSAVEDC_']
    opened_creature_action['Save Type'] = values['_CREATUREACTIONSAVETYPE_']
    opened_creature_action['Damage'] = window['_CreatureActionDamageList_'].get_list_values()
    opened_creature_action['Healing Roll'] = values['_CREATUREACTIONHEALINGROLL_']
    
    
        
    
    
layout_creature_actions_editor = [
    [sg.Text("Name", size=(8, 1)), sg.Input(size=(50, 1), key='_CREATUREACTIONNAME_', justification='left', enable_events=True)],
    [sg.Text("Attack Bonus", size=(12, 1)), sg.Input(size=(2, 1), key='_CREATUREACTIONATTACKBONUS_', justification='left', enable_events=True, visible=True)],
    [sg.Text("Save DC", size=(8, 1)), sg.Input(size=(2, 1), key='_CREATUREACTIONSAVEDC_', justification='left', enable_events=True, visible=True)],
    [sg.Text("Save Type", size=(8, 1)), sg.Combo(['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'], size=(5, 1), key='_CREATUREACTIONSAVETYPE_', visible=True)],
    [sg.Text("Damage (XdY+Z)", size=(13, 1)), sg.Input(size=(10, 1), key='_CREATUREACTIONDAMAGEROLL_', justification='left', enable_events=True, visible=True)],
    [sg.Text("Damage Type", size=(11, 1)), sg.Combo(values=damage_types, key='_CREATUREACTIONDAMAGETYPE_', enable_events=True, visible=True)],
    [sg.Button('Add Damage', use_ttk_buttons=True, visible=True, key='_CREATUREACTIONADDDAMAGE_'), sg.Button('Delete Damage', use_ttk_buttons=True, visible=True, key='_CREATUREACTIONDELETEDAMAGE_')],
    [sg.Listbox(values=[], size=(50, 5), key='_CreatureActionDamageList_')],
    [sg.Text("Healing (XdY+Z)", size=(13, 1)), sg.Input(size=(10, 1), key='_CREATUREACTIONHEALINGROLL_', justification='left', enable_events=True, visible=True)]
    
]

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
    'Resistances': [],
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
    'Resistances': [],
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
    window['_ResistanceModList_'].update(condition_data['Resistances'])
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
    condition_data['Resistances'] = window['_ResistanceModList_'].get_list_values()
    condition_data['Action Modifier'] = values['_ACTIONMOD_']
    condition_data['Bonus Action Modifier'] = values['_BONUSACTIONMOD_']
    condition_data['Reaction Modifier'] = values['_REACTIONMOD_']

base_action_data = {
    'Name': 'New Action',
    'Action Speed': 'Action',
    'Number of Targets': 1,
    'Target Type': 'Self',
    'Resource Cost': [],
    'Action Type': 'Attack Roll',
    'Effect': 'Damage',
    'Attack Bonus': 0,
    'Save DC': 10,
    'Save Type': 'STR',
    'Damage': [],
    'Healing Roll': '1d6+0',
    'Conditions': []
}

action_data = {
    'Name': None,
    'Action Speed': None,
    'Number of Targets': None,
    'Target Type': None,
    'Resource Cost': [],
    'Action Type': None,
    'Effect': None,
    'Attack Bonus': None,
    'Save DC': None,
    'Save Type': None,
    'Damage': [],
    'Healing Roll': None,
    'Conditions': []
}

def update_action(action_data):
    window['_ACTIONNAME_'].update(action_data['Name'])
    window['_ACTIONSPEED_'].update(action_data['Action Speed'])
    window['_NUMTARGETS_'].update(action_data['Number of Targets'])
    window['_TARGETTYPE_'].update(action_data['Target Type'])
    window['_ResourceCosts_'].update(action_data['Resource Cost'])
    window['_ACTIONTYPE_'].update(action_data['Action Type'])
    window['_EFFECT_'].update(action_data['Effect'])
    window['_ATTACKBONUS_'].update(action_data['Attack Bonus'])
    window['_SAVEDC_'].update(action_data['Save DC'])
    window['_SAVETYPE_'].update(action_data['Save Type'])
    if 'Damage' in action_data:
        window['_DamageList_'].update(action_data['Damage'])
    else:
        window['_DamageList_'].update([])
    window['_HEALINGROLL_'].update(action_data['Healing Roll'])
    window['_ConditionList_'].update(action_data['Conditions'])

def update_action_data(values):
    action_data['Name'] = values['_ACTIONNAME_']
    action_data['Action Speed'] = values['_ACTIONSPEED_']
    action_data['Number of Targets'] = values['_NUMTARGETS_']
    action_data['Target Type'] = values['_TARGETTYPE_']
    action_data['Resource Cost'] = window['_ResourceCosts_'].get_list_values()
    action_data['Action Type'] = values['_ACTIONTYPE_']
    action_data['Effect'] = values['_EFFECT_']
    action_data['Attack Bonus'] = values['_ATTACKBONUS_']
    action_data['Save DC'] = values['_SAVEDC_']
    action_data['Save Type'] = values['_SAVETYPE_']
    action_data['Damage'] = window['_DamageList_'].get_list_values()
    action_data['Healing Roll'] = values['_HEALINGROLL_']
    action_data['Conditions'] = window['_ConditionList_'].get_list_values()

simulation_data = {
    'Team1': [],
    'Team2': [],
    'Repetitions': 100
}


# Event loop
while True:
    event, values = window.read()
    #Closing Event
    if event == sg.WIN_CLOSED:
        break
    print(event)    
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
    elif event == 'Creature Stats':
        window['_CREATURE_'].update(visible=True)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_CREATURESTATS_'].update(visible=True)
        window['_CREATUREACTIONS_'].update(visible=False)
        window['_CREATURECOMBOS_'].update(visible=False)
        window['_CREATURERESOURCES_'].update(visible=False)
    elif event == 'Actions':
        window['_CREATURE_'].update(visible=True)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_CREATURESTATS_'].update(visible=False)
        window['_CREATUREACTIONS_'].update(visible=True)
        window['_CREATURECOMBOS_'].update(visible=False)
        window['_CREATURERESOURCES_'].update(visible=False)
    elif event == 'Resources':
        window['_CREATURE_'].update(visible=True)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_CREATURESTATS_'].update(visible=False)
        window['_CREATUREACTIONS_'].update(visible=False)
        window['_CREATURECOMBOS_'].update(visible=False)
        window['_CREATURERESOURCES_'].update(visible=True)
    elif event == 'Combos':
        window['_CREATURE_'].update(visible=True)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_CREATURESTATS_'].update(visible=False)
        window['_CREATUREACTIONS_'].update(visible=False)
        window['_CREATURECOMBOS_'].update(visible=True)
        window['_CREATURERESOURCES_'].update(visible=False)
    elif event == 'Action Stats':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=True)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_ACTIONSTATS_'].update(visible=True)
        window['_ACTIONCOSTS_'].update(visible=False)
        window['_ACTIONEFFECTS_'].update(visible=False)
    elif event == 'Costs':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=True)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_ACTIONSTATS_'].update(visible=False)
        window['_ACTIONCOSTS_'].update(visible=True)
        window['_ACTIONEFFECTS_'].update(visible=False)
    elif event == 'Effects':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=True)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_ACTIONSTATS_'].update(visible=False)
        window['_ACTIONCOSTS_'].update(visible=False)
        window['_ACTIONEFFECTS_'].update(visible=True)
    elif event == 'Condition Stats':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=True)
        window['_SIMULATOR_'].update(visible=False)
        window['_CONDITIONSTATS_'].update(visible=True)
        window['_CONDITIONOFFENSE_'].update(visible=False)
        window['_CONDITIONDEFENSE_'].update(visible=False)
        window['_CONDITIONECONOMY_'].update(visible=False)
    elif event == 'Offense Modifiers':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=True)
        window['_SIMULATOR_'].update(visible=False)
        window['_CONDITIONSTATS_'].update(visible=False)
        window['_CONDITIONOFFENSE_'].update(visible=True)
        window['_CONDITIONDEFENSE_'].update(visible=False)
        window['_CONDITIONECONOMY_'].update(visible=False)
    elif event == 'Defense Modifiers':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=True)
        window['_SIMULATOR_'].update(visible=False)
        window['_CONDITIONSTATS_'].update(visible=False)
        window['_CONDITIONOFFENSE_'].update(visible=False)
        window['_CONDITIONDEFENSE_'].update(visible=True)
        window['_CONDITIONECONOMY_'].update(visible=False)
    elif event == 'Economy Modifiers':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=True)
        window['_SIMULATOR_'].update(visible=False)
        window['_CONDITIONSTATS_'].update(visible=False)
        window['_CONDITIONOFFENSE_'].update(visible=False)
        window['_CONDITIONDEFENSE_'].update(visible=False)
        window['_CONDITIONECONOMY_'].update(visible=True)
    
    
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
    elif event == 'Delete Resource' and values['_ResourcesList_']:
        selected_resource = values['_ResourcesList_'][0]
        resource_data = window['_ResourcesList_'].get_list_values()
        resource_data.remove(selected_resource)
        window['_ResourcesList_'].update(resource_data)
    
    elif event == '_ActionList_' and len(values['_ActionList_']):
        print('test')
        selected_action = values['_ActionList_'][0]
        print(selected_action)
        opened_creature_action = selected_action
        update_creature_action(selected_action)
    elif event == 'Save Creature Action':
        update_creature_action_data(values)
        update_creature_data(values)

        # Show a file save dialog and get the chosen filename
        #filename = sg.popup_get_file('Save Creature Data', save_as=True, default_extension='.json', file_types=(('JSON Files', '*.json'),))
        filename = os.path.join(os.getcwd(),'Creatures')
        filename = os.path.join(filename,f"{creature_data['Name']}.json")
        
        if filename:
            save(filename, creature_data)
            sg.popup(f'Creature data saved to {filename}', title='Save Successful')      
    
    elif event == '_CREATUREACTIONADDDAMAGE_':
        damage_roll = values['_CREATUREACTIONDAMAGEROLL_']
        damage_type = values['_CREATUREACTIONDAMAGETYPE_']
        damage_data = window['_CreatureActionDamageList_'].get_list_values()
        damage_data.append({'Damage Roll': damage_roll, 'Damage Type': damage_type})
        window['_CreatureActionDamageList_'].update(damage_data)
    elif event == '_CREATUREACTIONDELETEDAMAGE_' and values['_CreatureActionDamageList_']:
        selected_damage = values['_CreatureActionDamageList_'][0]
        damage_data = window['_CreatureActionDamageList_'].get_list_values()
        damage_data.remove(selected_damage)
        window['_CreatureActionDamageList_'].update(damage_data)
    
    elif event == 'Add Creature Tag':
        tag = values['_CREATURETAG_']
        tag_data = window['_CreatureTagList_'].get_list_values()
        tag_data.append(tag)
        window['_CreatureTagList_'].update(tag_data)
    elif event == 'Delete Creature Tag':
        selected_tag = values['_CreatureTagList_'][0]
        tag_data = window['_CreatureTagList_'].get_list_values()
        tag_data.remove(selected_tag)
        window['_CreatureTagList_'].update(tag_data)
    elif event == 'Add Action':
        filename = sg.popup_get_file('Load Action Data', file_types=(('JSON Files', '*.json'),))
        if filename:
            action_data = load(filename)
            creature_data['Actions'].append(action_data)
            window['_ActionList_'].update(creature_data['Actions'])
    elif event == 'Delete Action' and values['_ActionList_']:
        selected_action = values['_ActionList_'][0]
        action_data = window['_ActionList_'].get_list_values()
        action_data.remove(selected_action)
        window['_ActionList_'].update(action_data)
    elif event == 'Add Combo':
        combo_data = window['_ComboList_'].get_list_values()
        combo_data.append(values['_COMBONAME_'])
        window['_ComboList_'].update(combo_data)
    elif event == 'Delete Combo' and values['_ComboList_']:
        selected_combo = values['_ComboList_'][0]
        combo_data = window['_ComboList_'].get_list_values()
        combo_data.remove(selected_combo)
        window['_ComboList_'].update(combo_data)
    elif event == 'Add Resistance/Vulnerability/Immunity':
        resistance_data = window['_ResistanceList_'].get_list_values()
        resistance_data.append([values['_DAMAGETYPERESISTANCE_'], values['_RESISTANCETYPE_']])
        window['_ResistanceList_'].update(resistance_data)
    elif event == 'Delete Resistance/Vulnerability/Immunity' and values['_ResistanceList_']:
        selected_resistance = values['_ResistanceList_'][0]
        resistance_data = window['_ResistanceList_'].get_list_values()
        resistance_data.remove(selected_resistance)
        window['_ResistanceList_'].update(resistance_data)
    elif event == 'Create New Creature':
        window['_CREATURES_'].update(values=get_creatures_list() + ['New Creature'])
        window['_CREATURES_'].set_value('New Creature')
        creature_data = base_creature_data
        update_creature(creature_data)
    elif event == 'Save Creature':# Update creature_data with input values
        update_creature_data(values)

        # Show a file save dialog and get the chosen filename
        #filename = sg.popup_get_file('Save Creature Data', save_as=True, default_extension='.json', file_types=(('JSON Files', '*.json'),))
        filename = os.path.join(os.getcwd(),'Creatures')
        filename = os.path.join(filename,f"{creature_data['Name']}.json")
        
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
    elif event == 'Add Resistance/Vulnerability/Immunity Modifier':
        resistance_data = window['_ResistanceModList_'].get_list_values()
        resistance_data.append([values['_DAMAGETYPERESISTANCEMOD_'], values['_RESISTANCETYPEMOD_']])
        window['_ResistanceModList_'].update(resistance_data)
    elif event == 'Delete Resistance/Vulnerability/Immunity Modifier' and values['_ResistanceModList_']:
        selected_resistance = values['_ResistanceModList_'][0]
        resistance_data = window['_ResistanceModList_'].get_list_values()
        resistance_data.remove(selected_resistance)
        window['_ResistanceModList_'].update(resistance_data)
    elif event == 'Save Condition':# Update condition_data with input values
        update_condition_data(values)

        # Show a file save dialog and get the chosen filename
        filename = sg.popup_get_file('Save Condition Data', save_as=True, default_extension='.json', file_types=(('JSON Files', '*.json'),))
        
        if filename:
            save(filename, condition_data)
            sg.popup(f'Condition data saved to {filename}', title='Save Successful')         
    elif event == 'Load Condition':
        # Show a file open dialog and get the chosen filename
        #filename = sg.popup_get_file('Load Condition Data', file_types=(('JSON Files', '*.json'),))
        filename = os.path.join(os.getcwd(),'Conditions')
        filename = os.path.join(filename,f"{condition_data['Name']}.json")
        
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
        window['_HEALINGROLL_'].update(visible=action_data['Effect'] == 'Healing')
        window['_ADDCONDITION_'].update(visible=action_data['Effect'] == 'Apply Condition')
        window['_DELETECONDITION_'].update(visible=action_data['Effect'] == 'Apply Condition')
        window['_ConditionList_'].update(visible=action_data['Effect'] == 'Apply Condition')
    elif event == '_ACTIONTYPE_':
        window['_ATTACKBONUS_'].update(visible=values['_ACTIONTYPE_'] == 'Attack Roll')
        window['_SAVEDC_'].update(visible=values['_ACTIONTYPE_'] == 'Saving Throw')
        window['_SAVETYPE_'].update(visible=values['_ACTIONTYPE_'] == 'Saving Throw')
    elif event == '_EFFECT_':
        window['_DAMAGEROLL_'].update(visible=values['_EFFECT_'] == 'Damage')
        window['_DAMAGETYPE_'].update(visible=values['_EFFECT_'] == 'Damage')
        window['_HEALINGROLL_'].update(visible=values['_EFFECT_'] == 'Healing')
        window['_ADDCONDITION_'].update(visible=values['_EFFECT_'] == 'Apply Condition')
        window['_DELETECONDITION_'].update(visible=values['_EFFECT_'] == 'Apply Condition')
        window['_ConditionList_'].update(visible=values['_EFFECT_'] == 'Apply Condition')
    elif event == '_ADDDAMAGE_':
        damage_roll = values['_DAMAGEROLL_']
        damage_type = values['_DAMAGETYPE_']
        damage_data = window['_DamageList_'].get_list_values()
        damage_data.append({'Damage Roll': damage_roll, 'Damage Type': damage_type})
        window['_DamageList_'].update(damage_data)
    elif event == '_DELETEDAMAGE_' and values['_DamageList_']:
        selected_action = values['_DamageList_'][0]
        damage_data = window['_DamageList_'].get_list_values()
        damage_data.remove(selected_action)
        window['_DamageList_'].update(damage_data)
    elif event == '_ADDCONDITION_':
        filename = sg.popup_get_file('Load Condition Data', file_types=(('JSON Files', '*.json'),))
        if filename:
            condition_data = load(filename)
            action_data['Conditions'].append(condition_data)
            window['_ConditionList_'].update(action_data['Conditions'])
    elif event == '_DELETECONDITION_' and values['_ConditionList_']:
        selected_condition = values['_ConditionList_'][0]
        condition_data = window['_ConditionList_'].get_list_values()
        condition_data.remove(selected_condition)
        window['_ConditionList_'].update(condition_data)
    elif event == 'Add Cost':
        name = values['_ACTIONRESOURCENAME_']
        number = values['_ACTIONRESOURCECOST_']
        resource_data = window['_ResourceCosts_'].get_list_values()
        resource_data.append({'Name': name, 'Number': number})
        window['_ResourceCosts_'].update(resource_data)
    elif event == 'Delete Cost' and values['_ResourceCosts_']:
        selected_cost = values['_ResourceCosts_'][0]
        cost_data = window['_ResourceCosts_'].get_list_values()
        cost_data.remove(selected_cost)
        window['_ResourceCosts_'].update(cost_data)
    elif event == 'Create New Action':
        window['_ACTIONS_'].update(values=get_actions_list() + ['New Action'])
        window['_ACTIONS_'].set_value('New Action')
        action_data = base_action_data
        update_action(action_data)
    elif event == 'Save Action':
        print(values)
        update_action_data(values)

        #filename = sg.popup_get_file('Save Action Data', save_as=True, default_extension='.json', file_types=(('JSON Files', '*.json'),))
        filename = os.path.join(os.getcwd(),'Actions')
        filename = os.path.join(filename,f"{action_data['Name']}.json")
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
        winratetext = run_simulation(simulation_data['Team1'], simulation_data['Team2'], simulation_data['Repetitions'])
        window['_SIMULATIONRESULTS_'].update(winratetext)
    
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