import PySimpleGUI as sg
import json
import os
import re
import copy
from simulator import Simulator
from creature import Creature
from action import Action, Attack_Roll, Auto_Apply, Saving_Throw, Damage, Healing, Apply_Condition
from conditions import Condition, Condition_Effect, Modified_Attack, Modified_Defense, Modified_Economy, Effect_Over_Time
import logger
import logging
import time

sg.theme('SystemDefaultForReal')
ttk_style = 'vista'
simulator = Simulator()

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

opened_creature_action = None

#Function to format damage and healing from XdY+Z format into a useable format
def format_roll(roll):
    roll_list = list(map(int,re.split('[d\+]', roll)))
    if len(roll_list) == 1:
        roll_list = [0,0,roll_list[0]]
    elif len(roll_list) == 2:
        roll_list.append(0)
    return roll_list

#Function to format conditions from the interface to the simulator.
def format_condition(condition):
    effectslist = []
    print(condition['Name'])
    if condition['Attack Modifier'] or condition['Attack Advantage'] or condition['Damage Modifier'] or condition['Crits On'] != 20 or condition['Extra Damage Roll']:
        if condition['Attack Advantage'] == 'Advantage': advantage = 1
        elif condition['Attack Advantage'] == 'Disadvantage': advantage = -1
        else: advantage = 0
        extra_damage = []
        if condition['Extra Damage Roll'] and condition['Extra Damage Type']:
            extra_damage = format_roll(condition['Extra Damage Roll']).append(condition['Extra Damage Type'])
        effectslist.append(Modified_Attack(int(condition['Attack Modifier']), int(condition['Damage Modifier']), advantage, extra_damage = extra_damage, crit_threshold = int(condition['Crits On'])))
    if condition['AC Modifier'] or condition['Defense Advantage'] or condition['Saves Modifier'] or condition['Saves Advantage'] or condition['Resistances'] or condition['Auto Crit'] == "True" or condition['Evasion']:
        if condition['Defense Advantage'] == 'Advantage': advantage = 1
        elif condition['Defense Advantage'] == 'Disadvantage': advantage = -1
        else: advantage = 0
        resistances = {}
        for resistance in condition['Resistances']:
            resistances[resistance[0]] = damage_multiplier[resistance[1]]
        if not 'Evasion' in condition:
            condition['Evasion'] = ['False','False','False','False','False','False']
        effectslist.append(Modified_Defense(int(condition['AC Modifier']), advantage, list(map(int, condition['Saves Modifier'])), condition['Saves Advantage'], resistances, auto_crit = condition['Auto Crit'] == 'True', evasion=list(map(lambda x: x == 'True', condition['Evasion']))))
    if condition['Action Modifier'] or condition['Bonus Action Modifier'] or condition['Reaction Modifier']:
        effectslist.append(Modified_Economy(int(condition['Action Modifier']), int(condition['Bonus Action Modifier']), int(condition['Reaction Modifier'])))
    if condition['Damage Over Time Roll'] or condition['Healing Over Time']:
        damage_over_time = []
        healing_over_time = []
        if condition['Healing Over Time']:
            healing_over_time = format_roll(condition['Healing Over Time'])
        if condition['Damage Over Time Roll']:
            damage_over_time = format_roll(condition['Damage Over Time Roll']).append(condition['Damage Over Time Type'])
        effectslist.append(Effect_Over_Time(damage_over_time, healing_over_time))
    paired = False
    if 'Paired Condition' in condition:
        if condition['Paired Condition'] == 'True': paired = True
    if condition['Duration'] == 'Permanent':
        return Condition(condition['Name'], 'Permanent', 9999, effectslist, is_paired = paired)
    return Condition(condition['Name'], condition['End Type'], int(condition['Duration']), effectslist, is_paired = paired)
        
def format_action(action, creature):
    effect = None
    is_concentration = False
    if action['Effect'] == 'Damage':
        total_damage = []
        for damage in action['Damage']:
            damage_formatted = format_roll(damage['Damage Roll'])
            damage_formatted.append(damage['Damage Type'])
            total_damage.append(damage_formatted)
            formatted_actions = []
            for follow_action in action['Follow Actions']:
                formatted_actions.append(format_action(follow_action, creature))
            if action['Follow Action']:
                for follow_action in creature['Actions']:
                    if follow_action['Name'] == action['Follow Action']:
                        formatted_actions.append(format_action(follow_action, creature))
        effect = Damage(total_damage, formatted_actions)
    elif action['Effect'] == 'Healing':
        healing_roll = format_roll(action['Healing Roll'])
        effect = Healing(int(healing_roll[0]), int(healing_roll[1]), int(healing_roll[2]))
    elif action['Effect'] == 'Apply Condition':
        for condition in action['Conditions']:
            formatted_condition = format_condition(condition)
            effect = Apply_Condition(formatted_condition, action['Concentration'] == "True")
            print(f'{action["Name"]}: {action["Concentration"]}')
            is_concentration = action['Concentration'] == "True"
    if action['Action Type'] == 'Attack Roll':
        attempt = Attack_Roll(int(action['Attack Bonus']), effect)
    elif action['Action Type'] == 'Saving Throw':
        half_on_save = True
        if action['Effect'] == 'Damage':
            if action['Half On Save'] == 'False': half_on_save = False
        attempt = Saving_Throw(int(action['Save DC']), saves_dict[action['Save Type']], half_on_save, effect)
    elif action['Action Type'] == 'Auto Apply':
        attempt = Auto_Apply(effect)
    resourcecost = None
    for resource in action['Resource Cost']:
        resourcecost = [resource['Name'], int(resource['Number'])]
    return Action(action['Name'], int(action['Number of Targets']), action['Target Type'], attempt, resourcecost, is_concentration = is_concentration)

#Function to format creatures from the interface to the simulator
def format_creature(creature):
    actionlist = []
    bonusactionlist = []
    freeactionlist = []
    for action in creature['Actions']:
        formatted_action = format_action(action, creature)
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
    for condition in creature['Conditions']:
        formatted_condition = format_condition(condition)
        formatted_condition.end_condition = 'Permanent'
        formatted_creature.add_permanent_condition(formatted_condition)
        formatted_condition.add_caster_target(formatted_creature,formatted_creature)
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
    open('Battle Log.txt', 'w').close()
    #Formatting creatures
    start = time.time()
    formatted_team1 = []
    formatted_team2 = []
    namelist = []
    repeated_names = []
    winrate1 = 0
    winrate2 = 0
    deaths_total = {}
    uncertainty_total = 0
    duration_total = 0
    permanency_team1 = 0
    permanency_team2 = 0
    biggest_advantages = []
    
    for creature in team1:
        formatted_team1.append(format_creature(creature))
        if creature['Name'] in namelist: repeated_names.append(creature['Name'])
        else: namelist.append(creature['Name'])
    for name in repeated_names:
        i = 1
        for creature in formatted_team1:
            if creature.name == name:
                creature.name += ' ' + str(i)
                i += 1
    for creature in team2:
        formatted_team2.append(format_creature(creature))
        if creature['Name'] in namelist: repeated_names.append(creature['Name'])
        else: namelist.append(creature['Name'])
    for name in repeated_names:
        i = 1
        for creature in formatted_team2:
            if creature.name == name:
                creature.name += ' ' + str(i)
                i += 1
    for i in range(iterations):
        for creature in formatted_team1:
            creature.full_restore()
        for creature in formatted_team2:
            creature.full_restore()
        response = simulator.start_simulation(formatted_team1.copy(),formatted_team2.copy())
        
        
        #Calculando métricas
        scores = response['scores']
        advantage_record = response['advantage_record']
        advantage_record = [i for i in advantage_record if i != 0]
        biggest_advantage = response['biggest_advantage']
        deaths = response['deaths']
        rounds = response['rounds']
        
        for death in deaths:
            if death in deaths_total:
                deaths_total[death] += 1
            else:
                deaths_total[death] = 1
                
        logging.info(f'Mortes: {deaths}')
        
        #Incerteza
        uncertainty = 0
        for i in range(1, len(advantage_record)):
            if advantage_record[i] != advantage_record[i - 1]:
                uncertainty += 1
        uncertainty = uncertainty/rounds
        logging.info(f'Incerteza: {uncertainty}')
        uncertainty_total += uncertainty
        
        #Duração
        duration_total += rounds
        logging.info(f'Duração: {rounds} rounds')
        
        #Permanencia
        leader_rounds = 1
        permanency_amount = 1
        leader_id = advantage_record[0]
        permanency_leader = leader_id

        for i in range(1, len(advantage_record)):
            if advantage_record[i] == advantage_record[i - 1]:
                leader_rounds += 1
            else:
                if leader_rounds > permanency_amount:
                    permanency_amount = leader_rounds
                    permanency_leader = leader_id

                leader_rounds = 1
                leader_id = advantage_record[i]

        # Ultimo líder
        if leader_rounds > permanency_amount:
            permanency_amount = leader_rounds
            permanency_leader = leader_id
        
        if permanency_leader == 1:
            permanency_team1 += permanency_amount/rounds
        elif permanency_leader == 2:
            permanency_team2 += permanency_amount/rounds
        logging.info(f'A maior permanência foi de {permanency_amount} rounds pelo time {permanency_leader}.\nPermanência de {100*permanency_amount/rounds}%')
        
        
        #Desafio
        winner = response['winner']
        if winner == 1:
            winrate1 += 1
        elif winner == 2:
            winrate2 += 1    
    
        #Vantagem Decisiva (da iteração)
        biggest_advantages.append([biggest_advantage,winner])
        logging.info(f'A maior vantagem foi de {biggest_advantage}\n')
        
    #Vantagem Decisiva (geral)
    biggest_positive_winner_2 = 0
    biggest_negative_winner_1 = 0
    for biggest_advantage, winner in biggest_advantages:
        if winner == 2 and biggest_advantage > biggest_positive_winner_2:
            biggest_positive_winner_2 = biggest_advantage
        elif winner == 1 and biggest_advantage < biggest_negative_winner_1:
            biggest_negative_winner_1 = biggest_advantage
    guaranteed_wins_1 = [biggest_advantage for biggest_advantage, winner in biggest_advantages if (biggest_advantage > biggest_positive_winner_2 and winner == 1)]
    guaranteed_wins_2 = [biggest_advantage for biggest_advantage, winner in biggest_advantages if (biggest_advantage < biggest_negative_winner_1 and winner == 2)]
    decisive_advantage_1 = 'N/A'
    decisive_advantage_2 = 'N/A'
    if guaranteed_wins_1: decisive_advantage_1 = min(guaranteed_wins_1)
    if guaranteed_wins_2: decisive_advantage_2 = max(guaranteed_wins_2)
        
    
    logging.info('Team 1 winrate: ' + str(round(winrate1*100/iterations,2)) + '%\nTeam 2 winrate: ' + str(round(winrate2*100/iterations,2)) + '%')
    logging.info(f'Duração média: {duration_total/iterations} rounds')
    logging.info(f'mortes (totais): {deaths_total}')
    logging.info(f'Incerteza média: {uncertainty_total/iterations}')
    logging.info(f'Permanencia média do time 1: {permanency_team1/iterations}')
    logging.info(f'Permanencia média do time 2: {permanency_team2/iterations}')
    logging.info(f'Vantagem Decisiva para time 1: {decisive_advantage_1}')
    logging.info(f'Vantagem Decisiva para time 2: {decisive_advantage_2}')
    end = time.time()
    logging.info(f'Tempo de execução: {end-start}')
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
    [sg.Text("AI", size=(2,1)), sg.DropDown(values=['Damage','Tank','Support', 'Neutral'], size=(7,1), key='_AI_')],
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
    [sg.Listbox(values=[], size=(50, 20), key='_ComboList_')]

]

layout_creature_actions_editor = [
    [sg.Text("Name", size=(8, 1)), sg.Input(size=(50, 1), key='_CREATUREACTIONNAME_', justification='left', enable_events=True)],
    [sg.pin(sg.Text("Attack Bonus", size=(12, 1), key='_CREATUREACTIONATTACKONLY_', visible=False)), sg.pin(sg.Input(size=(2, 1), key='_CREATUREACTIONATTACKBONUS_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Text("Save DC", size=(8, 1), key='_CREATUREACTIONSAVEONLYDC_', visible=False)), sg.pin(sg.Input(size=(2, 1), key='_CREATUREACTIONSAVEDC_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Text("Save Type", size=(8, 1), key='_CREATUREACTIONSAVEONLYTYPE_', visible=False)), sg.pin(sg.Combo(['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'], size=(5, 1), key='_CREATUREACTIONSAVETYPE_', visible=False))],
    [sg.pin(sg.Text("Damage (XdY+Z)", size=(13, 1), key='_CREATUREACTIONDAMAGEONLYDAMAGE_', visible=False)), sg.pin(sg.Input(size=(10, 1), key='_CREATUREACTIONDAMAGEROLL_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Text("Damage Type", size=(11, 1), key='_CREATUREACTIONDAMAGEONLYTYPE_', visible=False)), sg.pin(sg.Combo(values=damage_types, key='_CREATUREACTIONDAMAGETYPE_', enable_events=True, visible=False))],
    [sg.pin(sg.Button('Add Damage', use_ttk_buttons=True, visible=False, key='_CREATUREACTIONADDDAMAGE_')), sg.pin(sg.Button('Delete Damage', use_ttk_buttons=True, visible=False, key='_CREATUREACTIONDELETEDAMAGE_'))],
    [sg.pin(sg.Listbox(values=[], size=(50, 5), key='_CreatureActionDamageList_', visible=False))],
    [sg.pin(sg.Text("Healing (XdY+Z)", size=(13, 1), key='_CREATUREACTIONHEALINGONLY_', visible=False)), sg.pin(sg.Input(size=(10, 1), key='_CREATUREACTIONHEALINGROLL_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Text("Follow-up Action: ", key='_CREATUREACTIONFOLLOWUPTEXT_', visible=True)), sg.pin(sg.Input(size=(15,1), key='_CREATUREACTIONFOLLOWUP_', enable_events=True, visible=True))],
    [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Creature Action')]
]

layout_creature_actions_sidebar = [
    [sg.Listbox(values=[], size=(20, 30), key='_ActionList_', enable_events=True)],
    [sg.Button('Add Action', use_ttk_buttons=True), sg.Button('Delete Action', use_ttk_buttons=True)]
]



layout_creature_actions = [
    [sg.Column(layout_creature_actions_sidebar, element_justification='c'), sg.VerticalSeparator(), sg.Column(layout_creature_actions_editor)]
]

layout_creature_conditions = [
    [sg.Text("Conditions")],
    [sg.Button('Add Condition', use_ttk_buttons=True, key='_ADDCREATURECONDITION_'), sg.Button('Delete Condition', use_ttk_buttons=True, key='_DELETECREATURECONDITION_')],
    [sg.Listbox(values=[], size=(50, 5), key='_CreatureConditionList_')]
]

layout_creature_stats = [
    [sg.Column(layout_creature_statistics, key='_CREATURESTATS_', visible=True),
    sg.Column(layout_creature_actions, key='_CREATUREACTIONS_', visible=False),
    sg.Column(layout_creature_combos, key='_CREATURECOMBOS_', visible=False),
    sg.Column(layout_creature_resources, key='_CREATURERESOURCES_', visible=False),
    sg.Column(layout_creature_conditions, key='_CREATURECONDITIONS_', visible=False)],
    
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
    [sg.Text("Duration", size=(8,1)), sg.DropDown([1,2,10,100,'Permanent'], size=(5,1), key='_DURATION_'), 
    sg.Text('Turns, ends on', size=(14,1)), sg.DropDown(values=condition_end_possibilities, key='_ENDTYPE_')],
    [sg.Text("Paired Condition?"), sg.DropDown(values=['True','False'], size=(5,1), key='_PAIREDCONDITION_')],
]

layout_condition_offenses = [
    [sg.Text("Attack modifier", size=(15,1)), sg.Input(size=(3,1), key='_ATTACKMOD_'), 
    sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ATTACKADVANTAGE_'),
    sg.Text("Damage modifier", size=(15,1)), sg.Input(size=(3,1), key='_DAMAGEMOD_'),
    sg.Text("Crits on:", size=(8,1)), sg.Input(size=(3,1), key='_CRITSON_')],
    [sg.Text("Extra Damage")],
    [sg.Text("Damage (XdY+Z)", size=(13, 1)), sg.Input(size=(10, 1), key='_EXTRADAMAGEROLL_'), sg.DropDown(values=damage_types, key='_EXTRADAMAGETYPE_')],
    
]

layout_condition_defenses = [
    [sg.Text("AC modifier", size=(11,1)), sg.Input(size=(3,1), key='_ACMOD_'),
    sg.Text("Attacks against made at", size=(23,1)), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_DEFENSEADVANTAGE_')],
    [sg.Text("Auto crit?", size=(10,1)), sg.DropDown(values=['True','False'], size=(5,1), key='_AUTOCRIT_')],
    [sg.Text("Saving Throw Modifiers", size=(21,1))],
    [sg.Text("STR", size=(3,1)), sg.Input(size=(3,1), key='_ST1MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST1ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.DropDown(values=['True','False'], size=(5,1), key='_ST1EVASION_')],
    [sg.Text("DEX", size=(3,1)), sg.Input(size=(3,1), key='_ST2MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST2ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.DropDown(values=['True','False'], size=(5,1), key='_ST2EVASION_')],
    [sg.Text("CON", size=(3,1)), sg.Input(size=(3,1), key='_ST3MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST3ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.DropDown(values=['True','False'], size=(5,1), key='_ST3EVASION_')],
    [sg.Text("INT", size=(3,1)), sg.Input(size=(3,1), key='_ST4MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST4ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.DropDown(values=['True','False'], size=(5,1), key='_ST4EVASION_')],
    [sg.Text("WIS", size=(3,1)), sg.Input(size=(3,1), key='_ST5MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST5ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.DropDown(values=['True','False'], size=(5,1), key='_ST5EVASION_')],
    [sg.Text("CHA", size=(3,1)), sg.Input(size=(3,1), key='_ST6MOD_'), sg.DropDown(values=['','Advantage','Disadvantage'], size=(12,1), key='_ST6ADVANTAGE_'), sg.Text("Evasion?", size=(8,1)), sg.DropDown(values=['True','False'], size=(5,1), key='_ST6EVASION_')],
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

layout_condition_over_time = [
    [sg.Text("Damage over time")],
    [sg.Text("Damage (XdY+Z)", size=(13, 1)), sg.Input(size=(10, 1), key='_DAMAGEOVERTIMEROLL_'), sg.DropDown(values=damage_types, key='_DAMAGEOVERTIMETYPE_')],
    [sg.Text("Healing over time (XdY+Z)"), sg.Input(size=(10, 1), key='_HEALINGOVERTIMEROLL_')],
]

layout_conditions_stats = [
    [sg.Column(layout_condition_statistics, key='_CONDITIONSTATS_', visible=True),
    sg.Column(layout_condition_offenses, key='_CONDITIONOFFENSE_', visible=False),
    sg.Column(layout_condition_defenses, key='_CONDITIONDEFENSE_', visible=False),
    sg.Column(layout_condition_economy, key='_CONDITIONECONOMY_', visible=False),
    sg.Column(layout_condition_over_time, key='_CONDITIONOVERTIME_', visible=False)],
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
    [sg.Text("Action Speed", size=(12,1)), sg.Combo(['Action', 'Bonus Action', 'Free Action', 'Follow-Up'], size=(12, 1), key='_ACTIONSPEED_')],
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
    [sg.pin(sg.Text("Attack Bonus", size=(12, 1), key='_ATTACKONLY_', visible=False)), sg.pin(sg.Input(size=(2, 1), key='_ATTACKBONUS_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Text("Save DC", size=(8, 1), key='_SAVEONLYDC_', visible=False)), sg.pin(sg.Input(size=(2, 1), key='_SAVEDC_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Text("Save Type", size=(8, 1), key='_SAVEONLYTYPE_', visible=False)), sg.pin(sg.Combo(['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'], size=(5, 1), key='_SAVETYPE_', visible=False))],
    [sg.Text("Effect", size=(8, 1)), sg.Combo(['Damage', 'Healing', 'Apply Condition'], size=(12, 1), key='_EFFECT_', enable_events=True)],
    [sg.pin(sg.Text("Half on Save?", key='_HALFONSAVETEXT_', visible=False)), sg.pin(sg.DropDown(['True','False'], size=(5,1), key='_HALFONSAVE_', visible=False))],
    [sg.pin(sg.Text("Damage (XdY+Z)", size=(13, 1), key='_DAMAGEONLY_', visible=False)), sg.pin(sg.Input(size=(10, 1), key='_DAMAGEROLL_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Text("Damage Type", size=(11, 1), key='_DAMAGEONLY_', visible=False)), sg.pin(sg.Combo(values=damage_types, key='_DAMAGETYPE_', enable_events=True, visible=False))],
    [sg.pin(sg.Button('Add Damage', use_ttk_buttons=True, visible=False, key='_ADDDAMAGE_')), sg.pin(sg.Button('Delete Damage', use_ttk_buttons=True, visible=False, key='_DELETEDAMAGE_'))],
    [sg.pin(sg.Listbox(values=[], size=(50, 5), key='_DamageList_', visible=False))],
    [sg.pin(sg.Text("Healing (XdY+Z)", size=(13, 1), key='_HEALINGONLY_', visible=False)), sg.pin(sg.Input(size=(10, 1), key='_HEALINGROLL_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Button('Add Condition', use_ttk_buttons=True, visible=False, key='_ADDCONDITION_')), sg.pin(sg.Button('Delete Condition', use_ttk_buttons=True, visible=False, key='_DELETECONDITION_'))],
    [sg.pin(sg.Listbox(values=[], size=(50, 5), key='_ConditionList_', visible=False))],
    [sg.pin(sg.Text("Concentration", key='_CONDITIONONLY_', visible=False)), sg.pin(sg.DropDown(['True','False'], size=(5,1), key='_CONCENTRATION_', visible=False))]
]

layout_action_followups = [
    [sg.Text("Follow-up Actions")],
    [sg.Button('Add Follow-up Action', use_ttk_buttons=True, visible=True, key='_ADDFOLLOWUPACTION_'), sg.Button('Delete Follow-up Action', use_ttk_buttons=True, visible=True, key='_DELETEFOLLOWUPACTION_')],
    [sg.Listbox(values=[], size=(50, 5), key='_FollowupActionList_')]
]
    
layout_action_stats = [
    [sg.Column(layout_action_statistics, key='_ACTIONSTATS_', visible=True),
    sg.Column(layout_action_costs, key='_ACTIONCOSTS_', visible=False),
    sg.Column(layout_action_effects, key='_ACTIONEFFECTS_', visible=False),
    sg.Column(layout_action_followups, key='_ACTIONFOLLOWUPS_', visible = False)],
    
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
    [sg.Listbox(values=[], size=(20, 20), key='_TEAM1_', enable_events=True), sg.Listbox(values=[], size=(20, 20), key='_TEAM2_', enable_events=True)],
    [sg.Button('Add Creature to Team 1', use_ttk_buttons=True, key='Add Creature 1'), sg.Button('Add Creature to Team 2', use_ttk_buttons=True, key='Add Creature 2')],
    [sg.Button('Remove Creature from Team 1', use_ttk_buttons=True, key='Remove Creature 1'), sg.Button('Remove Creature from Team 2', use_ttk_buttons=True, key='Remove Creature 2')],
    [sg.Button('Simulate', use_ttk_buttons=True, key='Simulate')],
    [sg.Text("Results:", size=(8,1)), sg.Text('', key='_SIMULATIONRESULTS_')]
]

# Create the main window layout with the menu
layout_main = [
    [sg.Menu([['Creature', ['Creature Stats','Actions', 'Conditions', 'Resources', 'Combos']], ['Action',['Action Stats', 'Costs', 'Effects']], ['Condition',['Condition Stats', 'Offense Modifiers','Defense Modifiers', 'Economy Modifiers', 'Over Time']], ['Simulator',['Simulator']]])],
    [sg.Column(layout_creatures, key='_CREATURE_', visible=True),
     sg.Column(layout_actions, key='_ACTION_', visible=False),
     sg.Column(layout_conditions, key='_CONDITION_', visible=False),
     sg.Column(layout_simulator, key='_SIMULATOR_', visible=False)]
]

window = sg.Window('Menu Example', layout_main, ttk_theme=ttk_style, size=(800, 1000))  # Adjusted window size

base_creature_data = {
    'Name': 'New Creature',
    'HP': '1',
    'AC': '10',
    'Iniciative': '0',
    'Saving Throws': ['0', '0', '0', '0', '0', '0'],
    'Resources': [],
    'Actions': [],
    'Conditions': [],
    'Combos': [],
    'Resistances': [],
    'AI': 'Damage',
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
    'Conditions': [],
    'Combos': [],
    'Resistances': [],
    'AI': None,
    'Tags': [],
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
    if 'Conditions' in creature_data: window['_CreatureConditionList_'].update(creature_data['Conditions'])
    else: creature_data['Conditions'] = []
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
    creature_data['Conditions'] = window['_CreatureConditionList_'].get_list_values()
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
    window['_CREATUREACTIONFOLLOWUP_'].update(action['Follow Action'])
    
def update_creature_action_data(values):
    opened_creature_action['Name'] = values['_CREATUREACTIONNAME_']
    opened_creature_action['Attack Bonus'] = values['_CREATUREACTIONATTACKBONUS_']
    opened_creature_action['Save DC'] = values['_CREATUREACTIONSAVEDC_']
    opened_creature_action['Save Type'] = values['_CREATUREACTIONSAVETYPE_']
    opened_creature_action['Damage'] = window['_CreatureActionDamageList_'].get_list_values()
    opened_creature_action['Healing Roll'] = values['_CREATUREACTIONHEALINGROLL_']
    opened_creature_action['Follow Action'] = values['_CREATUREACTIONFOLLOWUP_']
    
    
        
    
    
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
    'Duration': '1',
    'Attack Modifier': '0',
    'Attack Advantage': '',
    'Crits On': '20',
    'Damage Modifier': '0',
    'Extra Damage Roll': '',
    'Extra Damage Type': '',
    'AC Modifier': '0',
    'Defense Advantage': '',
    'Auto Crit': 'False',
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
    'Evasion': ['False','False','False','False','False','False']
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

def update_condition(condition_data):
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
    for i in range(1, 7):
        window[f'_ST{i}MOD_'].update(condition_data['Saves Modifier'][i-1])
        window[f'_ST{i}ADVANTAGE_'].update(condition_data['Saves Advantage'][i-1])
        if 'Evasion' in condition_data: window[f'_ST{i}EVASION_'].update(condition_data['Evasion'][i-1])
        else: window[f'_ST{i}EVASION_'].update('False')
    window['_ResistanceModList_'].update(condition_data['Resistances'])
    window['_ACTIONMOD_'].update(condition_data['Action Modifier'])
    window['_BONUSACTIONMOD_'].update(condition_data['Bonus Action Modifier'])
    window['_REACTIONMOD_'].update(condition_data['Reaction Modifier'])
    window['_DAMAGEOVERTIMEROLL_'].update(condition_data['Damage Over Time Roll'])
    window['_DAMAGEOVERTIMETYPE_'].update(condition_data['Damage Over Time Type'])
    window['_HEALINGOVERTIMEROLL_'].update(condition_data['Healing Over Time'])
    if 'Paired Condition' in condition_data: window['_PAIREDCONDITION_'].update(condition_data['Paired Condition'])
    else: window['_PAIREDCONDITION_'].update('False')

def update_condition_data(values):
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

base_action_data = {
    'Name': 'New Action',
    'Action Speed': '',
    'Number of Targets': '',
    'Target Type': 'Self',
    'Resource Cost': [],
    'Action Type': '',
    'Effect': '',
    'Attack Bonus': '',
    'Save DC': '',
    'Save Type': '',
    'Half On Save': 'True',
    'Damage': [],
    'Healing Roll': '',
    'Conditions': [],
    'Concentration': 'False',
    'Follow Actions': [],
    'Follow Action': ''
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
    'Half On Save': None,
    'Damage': [],
    'Healing Roll': None,
    'Conditions': [],
    'Concentration': None,
    'Follow Actions': [],
    'Follow Action': ''
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
    if 'Half On Save' in action_data: window['_HALFONSAVE_'].update(action_data['Half On Save'])
    if 'Damage' in action_data:
        window['_DamageList_'].update(action_data['Damage'])
    else:
        window['_DamageList_'].update([])
    window['_HEALINGROLL_'].update(action_data['Healing Roll'])
    window['_ConditionList_'].update(action_data['Conditions'])
    if 'Concentration' in action_data: window['_CONCENTRATION_'].update(action_data['Concentration'])
    window['_FollowupActionList_'].update(action_data['Follow Actions'])

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
    action_data['Half On Save'] = values['_HALFONSAVE_']
    action_data['Damage'] = window['_DamageList_'].get_list_values()
    action_data['Healing Roll'] = values['_HEALINGROLL_']
    action_data['Conditions'] = window['_ConditionList_'].get_list_values()
    action_data['Concentration'] = values['_CONCENTRATION_']
    action_data['Follow Actions'] = window['_FollowupActionList_'].get_list_values()

simulation_data = {
    'Team1': [],
    'Team2': [],
    'Repetitions': 1000
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
        window['_CREATURECONDITIONS_'].update(visible=False)
        window['_CREATURECOMBOS_'].update(visible=False)
        window['_CREATURERESOURCES_'].update(visible=False)
    elif event == 'Actions':
        window['_CREATURE_'].update(visible=True)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_CREATURESTATS_'].update(visible=False)
        window['_CREATUREACTIONS_'].update(visible=True)
        window['_CREATURECONDITIONS_'].update(visible=False)
        window['_CREATURECOMBOS_'].update(visible=False)
        window['_CREATURERESOURCES_'].update(visible=False)
    elif event == 'Conditions':
        window['_CREATURE_'].update(visible=True)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_CREATURESTATS_'].update(visible=False)
        window['_CREATUREACTIONS_'].update(visible=False)
        window['_CREATURECONDITIONS_'].update(visible=True)
        window['_CREATURECOMBOS_'].update(visible=False)
        window['_CREATURERESOURCES_'].update(visible=False)
    elif event == 'Resources':
        window['_CREATURE_'].update(visible=True)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_CREATURESTATS_'].update(visible=False)
        window['_CREATUREACTIONS_'].update(visible=False)
        window['_CREATURECONDITIONS_'].update(visible=False)
        window['_CREATURECOMBOS_'].update(visible=False)
        window['_CREATURERESOURCES_'].update(visible=True)
    elif event == 'Combos':
        window['_CREATURE_'].update(visible=True)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_CREATURESTATS_'].update(visible=False)
        window['_CREATUREACTIONS_'].update(visible=False)
        window['_CREATURECONDITIONS_'].update(visible=False)
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
        window['_ACTIONFOLLOWUPS_'].update(visible=False)
    elif event == 'Costs':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=True)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_ACTIONSTATS_'].update(visible=False)
        window['_ACTIONCOSTS_'].update(visible=True)
        window['_ACTIONEFFECTS_'].update(visible=False)
        window['_ACTIONFOLLOWUPS_'].update(visible=False)
    elif event == 'Effects':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=True)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_ACTIONSTATS_'].update(visible=False)
        window['_ACTIONCOSTS_'].update(visible=False)
        window['_ACTIONEFFECTS_'].update(visible=True)
        window['_ACTIONFOLLOWUPS_'].update(visible=False)
    elif event == 'Follow-Ups':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=True)
        window['_CONDITION_'].update(visible=False)
        window['_SIMULATOR_'].update(visible=False)
        window['_ACTIONSTATS_'].update(visible=False)
        window['_ACTIONCOSTS_'].update(visible=False)
        window['_ACTIONEFFECTS_'].update(visible=False)
        window['_ACTIONFOLLOWUPS_'].update(visible=True)
    elif event == 'Condition Stats':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=True)
        window['_SIMULATOR_'].update(visible=False)
        window['_CONDITIONSTATS_'].update(visible=True)
        window['_CONDITIONOFFENSE_'].update(visible=False)
        window['_CONDITIONDEFENSE_'].update(visible=False)
        window['_CONDITIONECONOMY_'].update(visible=False)
        window['_CONDITIONOVERTIME_'].update(visible=False)
    elif event == 'Offense Modifiers':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=True)
        window['_SIMULATOR_'].update(visible=False)
        window['_CONDITIONSTATS_'].update(visible=False)
        window['_CONDITIONOFFENSE_'].update(visible=True)
        window['_CONDITIONDEFENSE_'].update(visible=False)
        window['_CONDITIONECONOMY_'].update(visible=False)
        window['_CONDITIONOVERTIME_'].update(visible=False)
    elif event == 'Defense Modifiers':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=True)
        window['_SIMULATOR_'].update(visible=False)
        window['_CONDITIONSTATS_'].update(visible=False)
        window['_CONDITIONOFFENSE_'].update(visible=False)
        window['_CONDITIONDEFENSE_'].update(visible=True)
        window['_CONDITIONECONOMY_'].update(visible=False)
        window['_CONDITIONOVERTIME_'].update(visible=False)
    elif event == 'Economy Modifiers':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=True)
        window['_SIMULATOR_'].update(visible=False)
        window['_CONDITIONSTATS_'].update(visible=False)
        window['_CONDITIONOFFENSE_'].update(visible=False)
        window['_CONDITIONDEFENSE_'].update(visible=False)
        window['_CONDITIONECONOMY_'].update(visible=True)
        window['_CONDITIONOVERTIME_'].update(visible=False)
    elif event == 'Over Time':
        window['_CREATURE_'].update(visible=False)
        window['_ACTION_'].update(visible=False)
        window['_CONDITION_'].update(visible=True)
        window['_SIMULATOR_'].update(visible=False)
        window['_CONDITIONSTATS_'].update(visible=False)
        window['_CONDITIONOFFENSE_'].update(visible=False)
        window['_CONDITIONDEFENSE_'].update(visible=False)
        window['_CONDITIONECONOMY_'].update(visible=False)
        window['_CONDITIONOVERTIME_'].update(visible=True)
    
    
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
        selected_action = values['_ActionList_'][0]
        opened_creature_action = selected_action
        update_creature_action(selected_action)
        window['_CREATUREACTIONATTACKONLY_'].update(visible=opened_creature_action['Action Type'] == 'Attack Roll')
        window['_CREATUREACTIONATTACKBONUS_'].update(visible=opened_creature_action['Action Type'] == 'Attack Roll')
        window['_CREATUREACTIONSAVEONLYDC_'].update(visible=opened_creature_action['Action Type'] == 'Saving Throw')
        window['_CREATUREACTIONSAVEDC_'].update(visible=opened_creature_action['Action Type'] == 'Saving Throw')
        window['_CREATUREACTIONSAVEONLYTYPE_'].update(visible=opened_creature_action['Action Type'] == 'Saving Throw')
        window['_CREATUREACTIONSAVETYPE_'].update(visible=opened_creature_action['Action Type'] == 'Saving Throw')
        window['_CREATUREACTIONDAMAGEONLYDAMAGE_'].update(visible=opened_creature_action['Effect'] == 'Damage')
        window['_CREATUREACTIONDAMAGEROLL_'].update(visible=opened_creature_action['Effect'] == 'Damage')
        window['_CREATUREACTIONDAMAGEONLYTYPE_'].update(visible=opened_creature_action['Effect'] == 'Damage')
        window['_CREATUREACTIONDAMAGETYPE_'].update(visible=opened_creature_action['Effect'] == 'Damage')
        window['_CREATUREACTIONADDDAMAGE_'].update(visible=opened_creature_action['Effect'] == 'Damage')
        window['_CREATUREACTIONDELETEDAMAGE_'].update(visible=opened_creature_action['Effect'] == 'Damage')
        window['_CreatureActionDamageList_'].update(visible=opened_creature_action['Effect'] == 'Damage')
        window['_CREATUREACTIONHEALINGONLY_'].update(visible=opened_creature_action['Effect'] == 'Healing')
        window['_CREATUREACTIONHEALINGROLL_'].update(visible=opened_creature_action['Effect'] == 'Healing')
        
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
        
    elif event == '_ADDCREATURECONDITION_':
        filename = sg.popup_get_file('Load Condition Data', file_types=(('JSON Files', '*.json'),))
        if filename:
            condition_data = load(filename)
            creature_data['Conditions'].append(condition_data)
            window['_CreatureConditionList_'].update(creature_data['Conditions'])
    elif event == '_DELETECREATURECONDITION_' and values['_CreatureConditionList_']:
        selected_condition = values['_CreatureConditionList_'][0]
        condition_data = window['_CreatureConditionList_'].get_list_values()
        condition_data.remove(selected_condition)
        window['_CreatureConditionList_'].update(condition_data)    
    
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
        creature_data = copy.deepcopy(base_creature_data)
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
            window.Element('_CREATURES_').Update(get_creatures_list())
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
        condition_data = copy.deepcopy(base_condition_data)
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
        update_condition_data(values)

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
        window['_ATTACKONLY_'].update(visible=action_data['Action Type'] == 'Attack Roll')
        window['_ATTACKBONUS_'].update(visible=action_data['Action Type'] == 'Attack Roll')
        window['_SAVEONLYDC_'].update(visible=action_data['Action Type'] == 'Saving Throw')
        window['_SAVEDC_'].update(visible=action_data['Action Type'] == 'Saving Throw')
        window['_SAVEONLYTYPE_'].update(visible=action_data['Action Type'] == 'Saving Throw')
        window['_SAVETYPE_'].update(visible=action_data['Action Type'] == 'Saving Throw')
        window['_HALFONSAVETEXT_'].update(visible=(action_data['Action Type'] == 'Saving Throw' and action_data['Effect'] == 'Damage'))
        window['_HALFONSAVE_'].update(visible=(action_data['Action Type'] == 'Saving Throw' and action_data['Effect'] == 'Damage'))
        window['_DAMAGEONLY_'].update(visible=action_data['Effect'] == 'Damage')
        window['_DAMAGEROLL_'].update(visible=action_data['Effect'] == 'Damage')
        window['_DAMAGETYPE_'].update(visible=action_data['Effect'] == 'Damage')
        window['_ADDDAMAGE_'].update(visible=action_data['Effect'] == 'Damage')
        window['_DELETEDAMAGE_'].update(visible=action_data['Effect'] == 'Damage')
        window['_DamageList_'].update(visible=action_data['Effect'] == 'Damage')
        window['_HEALINGONLY_'].update(visible=action_data['Effect'] == 'Healing')
        window['_HEALINGROLL_'].update(visible=action_data['Effect'] == 'Healing')
        window['_CONDITIONONLY_'].update(visible=action_data['Effect'] == 'Apply Condition')
        window['_ADDCONDITION_'].update(visible=action_data['Effect'] == 'Apply Condition')
        window['_DELETECONDITION_'].update(visible=action_data['Effect'] == 'Apply Condition')
        window['_ConditionList_'].update(visible=action_data['Effect'] == 'Apply Condition')
        window['_CONCENTRATION_'].update(visible=action_data['Effect'] == 'Apply Condition')
    elif event == '_ACTIONTYPE_':
        window['_ATTACKONLY_'].update(visible=values['_ACTIONTYPE_'] == 'Attack Roll')
        window['_ATTACKBONUS_'].update(visible=values['_ACTIONTYPE_'] == 'Attack Roll')
        window['_SAVEONLYDC_'].update(visible=values['_ACTIONTYPE_'] == 'Saving Throw')
        window['_SAVEDC_'].update(visible=values['_ACTIONTYPE_'] == 'Saving Throw')
        window['_SAVEONLYTYPE_'].update(visible=values['_ACTIONTYPE_'] == 'Saving Throw')
        window['_SAVETYPE_'].update(visible=values['_ACTIONTYPE_'] == 'Saving Throw')
        window['_HALFONSAVETEXT_'].update(visible=(values['_ACTIONTYPE_'] == 'Saving Throw' and values['_EFFECT_'] == 'Damage'))
        window['_HALFONSAVE_'].update(visible=(values['_ACTIONTYPE_'] == 'Saving Throw' and values['_EFFECT_'] == 'Damage'))
    elif event == '_EFFECT_':
        window['_DAMAGEONLY_'].update(visible=values['_EFFECT_'] == 'Damage')
        window['_DAMAGEROLL_'].update(visible=values['_EFFECT_'] == 'Damage')
        window['_DAMAGETYPE_'].update(visible=values['_EFFECT_'] == 'Damage')
        window['_ADDDAMAGE_'].update(visible=values['_EFFECT_'] == 'Damage')
        window['_DELETEDAMAGE_'].update(visible=values['_EFFECT_'] == 'Damage')
        window['_DamageList_'].update(visible=values['_EFFECT_'] == 'Damage')
        window['_HEALINGONLY_'].update(visible=values['_EFFECT_'] == 'Healing')
        window['_HEALINGROLL_'].update(visible=values['_EFFECT_'] == 'Healing')
        window['_CONDITIONONLY_'].update(visible=values['_EFFECT_'] == 'Apply Condition')
        window['_ADDCONDITION_'].update(visible=values['_EFFECT_'] == 'Apply Condition')
        window['_DELETECONDITION_'].update(visible=values['_EFFECT_'] == 'Apply Condition')
        window['_ConditionList_'].update(visible=values['_EFFECT_'] == 'Apply Condition')
        window['_CONCENTRATION_'].update(visible=values['_EFFECT_'] == 'Apply Condition')
    
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
        
    elif event == '_ADDFOLLOWUPACTION_':
        filename = sg.popup_get_file('Load Action Data', file_types=(('JSON Files', '*.json'),))
        if filename:
            follow_action_data = load(filename)
            action_data['Follow Actions'].append(follow_action_data)
            window['_FollowupActionList_'].update(action_data['Follow Actions'])
    elif event == '_DELETEFOLLOWUPACTION_' and values['_FollowupActionList_']:
        selected_action = values['_FollowupActionList_'][0]
        follow_action_data = window['_FollowupActionList_'].get_list_values()
        follow_action_data.remove(selected_action)
        window['_FollowupActionList_'].update(follow_action_data)
        
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
        action_data = copy.deepcopy(base_action_data)
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
            window.Element('_ACTIONS_').Update(get_actions_list())
    elif event == 'Load Action':
        filename = sg.popup_get_file('Load Action Data', file_types=(('JSON Files', '*.json'),))
        
        if filename:
            action_data = load(filename)
            update_action(action_data)
            sg.popup(f'Action data loaded from {filename}', title='Load Successful')
    
    #Simulator Events
    elif event == 'Add Creature 1':
        filenames = sg.popup_get_file('Load Creature Data', file_types=(('JSON Files', '*.json'),), multiple_files=True)
        if filenames:
            filename_list = filenames.split(";")
            for filename in filename_list:
                creature_data = load(filename)
                simulation_data['Team1'].append(creature_data)
                window['_TEAM1_'].update(simulation_data['Team1'])
    elif event == 'Add Creature 2':
        filenames = sg.popup_get_file('Load Creature Data', file_types=(('JSON Files', '*.json'),), multiple_files=True)
        if filenames:
            filename_list = filenames.split(";")
            for filename in filename_list:
                creature_data = load(filename)
                simulation_data['Team2'].append(creature_data)
                window['_TEAM2_'].update(simulation_data['Team2'])
            
    elif event == 'Remove Creature 1' and values['_TEAM1_']:
        selected_creature = values['_TEAM1_'][0]
        team_data = window['_TEAM1_'].get_list_values()
        team_data.remove(selected_creature)
        window['_TEAM1_'].update(team_data)
        simulation_data['Team1'] = window['_TEAM1_'].get_list_values()
    
    elif event == 'Remove Creature 2' and values['_TEAM2_']:
        selected_creature = values['_TEAM2_'][0]
        team_data = window['_TEAM2_'].get_list_values()
        team_data.remove(selected_creature)
        window['_TEAM2_'].update(team_data)  
        simulation_data['Team2'] = window['_TEAM2_'].get_list_values()      
            
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