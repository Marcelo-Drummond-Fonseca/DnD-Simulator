import PySimpleGUI as sg
from simulator import Simulator
from utilitiesUI import save, load, get_creatures_list
import formatter
import logger
import logging
import time
import os
import json

simulator = Simulator()

#Function to run the simulations
def run_simulation(team1, team2, team3, team4, rest1, rest2, iterations, full_logs):
    open('Battle Log.txt', 'w').close()
    if not full_logs: logging.disable()
    else: logging.disable(logging.NOTSET)
    #Formatting creatures
    start = time.time()
    formatted_team1 = []
    formatted_team2 = []
    formatted_team3 = []
    formatted_team4 = []
    namelist = []
    repeated_names = []
    winrate1_2 = 0
    winrate1_3 = 0
    winrate1_4 = 0
    winrate2 = 0
    winrate3 = 0
    winrate4 = 0
    battles_12 = 0
    battles_13 = 0
    battles_14 = 0
    deaths_total = {}
    uncertainty_total = 0
    duration_total = 0
    permanency_team1 = 0
    permanency_team2 = 0
    biggest_advantages = []
    hp_percents1_2 = 0
    hp_percents1_3 = 0
    hp_percents1_4 = 0
    hp_percents2 = 0
    
    for creature in team1:
        formatted_team1.append(formatter.format_creature(creature))
        if creature['Name'] in namelist: repeated_names.append(creature['Name'])
        else: namelist.append(creature['Name'])
    for name in repeated_names:
        i = 1
        for creature in formatted_team1:
            if creature.name == name:
                creature.name += ' ' + str(i)
                i += 1
    for creature in team2:
        formatted_team2.append(formatter.format_creature(creature))
        if creature['Name'] in namelist: repeated_names.append(creature['Name'])
        else: namelist.append(creature['Name'])
    for name in repeated_names:
        i = 1
        for creature in formatted_team2:
            if creature.name == name:
                creature.name += ' ' + str(i)
                i += 1
    for creature in team3:
        formatted_team3.append(formatter.format_creature(creature))
        if creature['Name'] in namelist: repeated_names.append(creature['Name'])
        else: namelist.append(creature['Name'])
    for name in repeated_names:
        i = 1
        for creature in formatted_team3:
            if creature.name == name:
                creature.name += ' ' + str(i)
                i += 1
    for creature in team4:
        formatted_team4.append(formatter.format_creature(creature))
        if creature['Name'] in namelist: repeated_names.append(creature['Name'])
        else: namelist.append(creature['Name'])
    for name in repeated_names:
        i = 1
        for creature in formatted_team4:
            if creature.name == name:
                creature.name += ' ' + str(i)
                i += 1
    
    for i in range(iterations):
        for creature in formatted_team1:
            creature.full_restore()
        for creature in formatted_team2:
            creature.full_restore()
        for creature in formatted_team3:
            creature.full_restore()
        for creature in formatted_team4:
            creature.full_restore()
        
        opponents = [formatted_team2]
        if formatted_team3: opponents.append(formatted_team3)
        if formatted_team4: opponents.append(formatted_team4)
        
        for index, opponent in enumerate(opponents):
        
            if index==0: battles_12 += 1
            if index==1: battles_13 += 1
            if index==2: battles_14 += 1
        
            if index == 1 and rest1 == 'No Rest':
                for creature in formatted_team1:
                    creature.lose_concentration()
                    creature.remove_all_conditions()
            elif index == 1 and rest1 == 'Short Rest':
                for creature in formatted_team1:
                    creature.lose_concentration()
                    creature.short_rest()
            if index == 2 and rest2 == 'No Rest':
                for creature in formatted_team1:
                    creature.lose_concentration()
                    creature.remove_all_conditions()
            elif index == 2 and rest2 == 'Short Rest':
                for creature in formatted_team1:
                    creature.lose_concentration()
                    creature.short_rest()
                
        
            response = simulator.start_simulation(formatted_team1.copy(),opponent.copy())
            
            
            #Calculando métricas
            scores = response['scores']
            advantage_record = response['advantage_record']
            advantage_record = [i for i in advantage_record if i != 0]
            biggest_advantage = response['biggest_advantage']
            deaths = response['deaths']
            rounds = response['rounds']
            hp_percent = response['HP percent']
            
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
                if index == 0: 
                    winrate1_2 += 1
                    hp_percents1_2 += hp_percent
                elif index == 1: 
                    winrate1_3 += 1
                    hp_percents1_3 += hp_percent
                elif index == 2: 
                    winrate1_4 += 1
                    hp_percents1_4 += hp_percent
            elif winner == 2:
                if index == 0: 
                    winrate2 += 1
                    hp_percents2 += hp_percent
                elif index == 1: winrate3 += 1  
                elif index == 2: winrate4 += 1   
        
            #Vantagem Decisiva (da iteração)
            biggest_advantages.append([biggest_advantage,winner])
            logging.info(f'A maior vantagem foi de {biggest_advantage}')
            logging.info(f'A porcentagem de HP restante do time vencedor foi {round(hp_percent*100,2)}%\n')
            
            if winner == 2:
                break
    
    logging.disable(logging.NOTSET)
    
    if len(opponents) == 1:
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
            
        
        logging.info('Team 1 winrate: ' + str(round(winrate1_2*100/iterations,2)) + '%\nTeam 2 winrate: ' + str(round(winrate2*100/iterations,2)) + '%')
        logging.info(f'Duração média: {duration_total/iterations} rounds')
        logging.info(f'mortes (totais): {deaths_total}')
        logging.info(f'Incerteza média: {uncertainty_total/iterations}')
        logging.info(f'Permanencia média do time 1: {permanency_team1/iterations}')
        logging.info(f'Permanencia média do time 2: {permanency_team2/iterations}')
        logging.info(f'Vantagem Decisiva para time 1: {decisive_advantage_1}')
        logging.info(f'Vantagem Decisiva para time 2: {decisive_advantage_2}')
        logging.info(f'Porcentagem de HP restante médio para time 1: {hp_percents1_2/winrate1_2 if winrate1_2 != 0 else 0}')
        logging.info(f'Porcentagem de HP restante médio para time 2: {hp_percents2/winrate2 if winrate2 != 0 else 0}')
        end = time.time()
        logging.info(f'Tempo de execução: {end-start}')
        return('Team 1 winrate: ' + str(round(winrate1_2*100/iterations,2)) + 
        '%\nTeam 2 winrate: ' + str(round(winrate2*100/iterations,2)) +
        '%\nAverage Duration (in rounds): ' + str(duration_total/iterations) +
        '\nTotal Deaths: ' + str(deaths_total) +
        '\nAverage remaining HP for Team 1 on a win: ' + str(round(hp_percents1_2/winrate1_2,2) if winrate1_2 != 0 else 0) +
        '\nAverage remaining HP for Team 2 on a win: ' + str(round(hp_percents2/winrate2,2) if winrate2 != 0 else 0))
        
    
    elif len(opponents) == 2:
        logging.info(f'Team 1 dungeon clear rate: {round(100*winrate1_3/iterations)}%')
        logging.info(f'mortes (totais): {deaths_total}')
        logging.info(f'Porcentagem de HP restante médio após primeiro combate: {hp_percents1_2/winrate1_2 if winrate1_2 != 0 else 0}')
        logging.info(f'Porcentagem de HP restante médio após segundo combate: {hp_percents1_3/winrate1_3 if winrate1_3 != 0 else 0}')
        return('Team 1 clear rate: ' + str(round(winrate1_3*100/iterations,2)) + '%' +
        '\nTotal Deaths: ' + str(deaths_total) +
        '\nAverage remaining HP for Team 1 after first combat: ' + str(round(hp_percents1_2/winrate1_2,2) if winrate1_2 != 0 else 0) +
        '%\nAverage remaining HP for Team 1 after second combat: ' + str(round(hp_percents1_3/winrate1_3,2) if winrate1_3 != 0 else 0) + '%')
        
        
    elif len(opponents) == 3:
        logging.info(f'Team 1 dungeon clear rate: {round(100*winrate1_4/iterations)}%')
        logging.info(f'mortes (totais): {deaths_total}')
        logging.info(f'Porcentagem de HP restante médio após primeiro combate: {hp_percents1_2/winrate1_2 if winrate1_2 != 0 else 0}')
        logging.info(f'Porcentagem de HP restante médio após segundo combate: {hp_percents1_3/winrate1_3 if winrate1_3 != 0 else 0}')
        logging.info(f'Porcentagem de HP restante médio após terceiro combate: {hp_percents1_4/winrate1_4 if winrate1_4 != 0 else 0}')
        return('Team 1 clear rate: ' + str(round(winrate1_4*100/iterations,2)) + '%' +
        '\nTotal Deaths: ' + str(deaths_total) +
        '\nAverage remaining HP for Team 1 after first combat: ' + str(round(hp_percents1_2/winrate1_2,2) if winrate1_2 != 0 else 0) +
        '%\nAverage remaining HP for Team 1 after second combat: ' + str(round(hp_percents1_3/winrate1_3,2) if winrate1_3 != 0 else 0) +
        '%\nAverage remaining HP for Team 1 after third combat: ' + str(round(hp_percents1_4/winrate1_4,2) if winrate1_4 != 0 else 0) + '%')


#SIMULATOR UI

layout_creatures_simulator_sidebar = [
    [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTCREATURESIMULATOR_', enable_events=True)],
    [sg.Listbox(values=get_creatures_list(), size=(20, 30), key='_CREATURESSIMULATOR_', enable_events=True)],
    [sg.Button('Add Selected to Team 1', use_ttk_buttons=True, key='Add Creature 1')],
    [sg.Button('Add Selected to Team 2', use_ttk_buttons=True, key='Add Creature 2')],
    [sg.Button('Add Selected to Team 3', use_ttk_buttons=True, key='Add Creature 3')],
    [sg.Button('Add Selected to Team 4', use_ttk_buttons=True, key='Add Creature 4')],
]

layout_simulator_team1 = [
    [sg.Text("Team 1")],
    [sg.Listbox(values=[], size=(20, 20), key='_TEAM1_', enable_events=True)],
    [sg.Button('Remove Selected from Team 1', use_ttk_buttons=True, key='Remove Creature 1')],
]

layout_simulator_team2 = [
    [sg.Text("Team 2")],
    [sg.Listbox(values=[], size=(20, 20), key='_TEAM2_', enable_events=True)],
    [sg.Button('Remove Selected from Team 2', use_ttk_buttons=True, key='Remove Creature 2')],
]

layout_simulator_team3 = [
    [sg.Text("Team 3")],
    [sg.Listbox(values=[], size=(20, 20), key='_TEAM3_', enable_events=True)],
    [sg.Button('Remove Selected from Team 3', use_ttk_buttons=True, key='Remove Creature 3')],
    [sg.Text('Time Between Fights?'),sg.DropDown(['Immediate','No Rest','Short Rest'], key='_REST1_')],
]

layout_simulator_team4 = [
    [sg.Text("Team 4")],
    [sg.Listbox(values=[], size=(20, 20), key='_TEAM4_', enable_events=True)],
    [sg.Button('Remove Selected from Team 4', use_ttk_buttons=True, key='Remove Creature 4')],
    [sg.Text('Time Between Fights?'),sg.DropDown(['Immediate','No Rest','Short Rest'], key='_REST2_')],
]

layout_simulator_main = [
    sg.vtop([sg.Column(layout_simulator_team1, element_justification='c'), sg.Column(layout_simulator_team2, element_justification='c'), sg.Column(layout_simulator_team3, element_justification='c'), sg.Column(layout_simulator_team4, element_justification='c')]),
#   [sg.Listbox(values=[], size=(20, 20), key='_TEAM1_', enable_events=True), sg.Listbox(values=[], size=(20, 20), key='_TEAM2_', enable_events=True),sg.DropDown(['Instant','No Rest','Short Rest'], key='_REST1_'), sg.Listbox(values=[], size=(20, 20), key='_TEAM3_', enable_events=True),sg.DropDown(['Instant','No Rest','Short Rest'], key='_REST2_'), sg.Listbox(values=[], size=(20, 20), key='_TEAM4_', enable_events=True)],
#   [sg.Button('Add Creature to Team 1', use_ttk_buttons=True, key='Add Creature 1'), sg.Button('Add Creature to Team 2', use_ttk_buttons=True, key='Add Creature 2'), sg.Button('Add Creature to Team 3', use_ttk_buttons=True, key='Add Creature 3'), sg.Button('Add Creature to Team 4', use_ttk_buttons=True, key='Add Creature 4')],
#   [sg.Button('Remove Creature from Team 1', use_ttk_buttons=True, key='Remove Creature 1'), sg.Button('Remove Creature from Team 2', use_ttk_buttons=True, key='Remove Creature 2'), sg.Button('Remove Creature from Team 3', use_ttk_buttons=True, key='Remove Creature 3'), sg.Button('Remove Creature from Team 4', use_ttk_buttons=True, key='Remove Creature 4')],
    [sg.Text('Number of Simulations:'), sg.Input(size=(5,1), key='_ITERATIONS_', enable_events=True, default_text='1000')],
    [sg.Text('Complete Logs?'),sg.Checkbox('', default=False, key='_FULLLOGS_', visible=True)],
    [sg.Button('Simulate', use_ttk_buttons=True, key='Simulate')],
    [sg.Text("Results:", size=(8,1)), sg.Text('', key='_SIMULATIONRESULTS_')],
    [sg.Button('Open Complete Logs', use_ttk_buttons=True, key='Logs_Button', visible=False)],
]

layout_simulator = [
    sg.vtop([sg.Column(layout_simulator_main), sg.VerticalSeparator(), sg.Column(layout_creatures_simulator_sidebar)])
]

# Create the main window layout with the menu
#layout_main = [
#    [sg.Menu([['Simulator',['Simulator']],['Creature', ['Creature Stats','Actions', 'Conditions', 'Resources', 'Combos']], ['Action',['Action Stats', 'Costs', 'Effects']], ['Condition',['Condition Stats', 'Offense Modifiers','Defense Modifiers', 'Economy Modifiers', 'Over Time']]])],
#    [sg.Column(layout_creatures, key='_CREATURE_', visible=False),
#     sg.Column(layout_actions, key='_ACTION_', visible=False),
#     sg.Column(layout_conditions, key='_CONDITION_', visible=False),
#     sg.Column(layout_simulator, key='_SIMULATOR_', visible=True)]
#]

simulation_data = {
    'Team1': [],
    'Team2': [],
    'Team3': [],
    'Team4': [],
    'Repetitions': 1000
}

def events(event, values,window):
    
    #Simulator Events
    if event == 'Add Creature 1' and values['_CREATURESSIMULATOR_']:
        selected_creature = values['_CREATURESSIMULATOR_'][0]
        filename = os.path.join(os.getcwd(), 'Creatures', selected_creature + '.json')
        creature_data = load(filename)
        simulation_data['Team1'].append(creature_data)
        window['_TEAM1_'].update(simulation_data['Team1'])
        #filenames = sg.popup_get_file('Load Creature Data', file_types=(('JSON Files', '*.json'),), multiple_files=True)
        #if filenames:
        #    filename_list = filenames.split(";")
        #    for filename in filename_list:
        #        creature_data = load(filename)
        #        simulation_data['Team1'].append(creature_data)
        #        window['_TEAM1_'].update(simulation_data['Team1'])
    elif event == 'Add Creature 2' and values['_CREATURESSIMULATOR_']:
        selected_creature = values['_CREATURESSIMULATOR_'][0]
        filename = os.path.join(os.getcwd(), 'Creatures', selected_creature + '.json')
        creature_data = load(filename)
        simulation_data['Team2'].append(creature_data)
        window['_TEAM2_'].update(simulation_data['Team2'])
    
        #filenames = sg.popup_get_file('Load Creature Data', file_types=(('JSON Files', '*.json'),), multiple_files=True)
        #if filenames:
        #    filename_list = filenames.split(";")
        #    for filename in filename_list:
        #        creature_data = load(filename)
        #        simulation_data['Team2'].append(creature_data)
        #        window['_TEAM2_'].update(simulation_data['Team2'])
    elif event == 'Add Creature 3' and values['_CREATURESSIMULATOR_']:
        selected_creature = values['_CREATURESSIMULATOR_'][0]
        filename = os.path.join(os.getcwd(), 'Creatures', selected_creature + '.json')
        creature_data = load(filename)
        simulation_data['Team3'].append(creature_data)
        window['_TEAM3_'].update(simulation_data['Team3'])
    elif event == 'Add Creature 4' and values['_CREATURESSIMULATOR_']:
        selected_creature = values['_CREATURESSIMULATOR_'][0]
        filename = os.path.join(os.getcwd(), 'Creatures', selected_creature + '.json')
        creature_data = load(filename)
        simulation_data['Team4'].append(creature_data)
        window['_TEAM4_'].update(simulation_data['Team4'])
            
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
    
    elif event == 'Remove Creature 3' and values['_TEAM3_']:
        selected_creature = values['_TEAM3_'][0]
        team_data = window['_TEAM3_'].get_list_values()
        team_data.remove(selected_creature)
        window['_TEAM3_'].update(team_data)  
        simulation_data['Team3'] = window['_TEAM3_'].get_list_values()  
    
    elif event == 'Remove Creature 4' and values['_TEAM4_']:
        selected_creature = values['_TEAM4_'][0]
        team_data = window['_TEAM4_'].get_list_values()
        team_data.remove(selected_creature)
        window['_TEAM4_'].update(team_data)  
        simulation_data['Team4'] = window['_TEAM4_'].get_list_values()    
            
    elif event == 'Simulate':
        iterations = int(values['_ITERATIONS_']) if values['_ITERATIONS_'] else 1
        full_logs = values['_FULLLOGS_']
        winratetext = run_simulation(simulation_data['Team1'], simulation_data['Team2'], simulation_data['Team3'], simulation_data['Team4'], values['_REST1_'],values['_REST2_'], iterations, full_logs)
        window['_SIMULATIONRESULTS_'].update(winratetext)
        window['Logs_Button'].update(visible=full_logs)
        
    elif event == 'Logs_Button':
        os.startfile('Battle Log.txt')
    
    elif event == '_CREATURESSIMULATOR_':
        pass
        
    elif values['_INPUTCREATURESIMULATOR_'] != '':
        search = values['_INPUTCREATURESIMULATOR_']
        new_values = [x for x in get_creatures_list() if search.lower() in x.lower()]
        window.Element('_CREATURESSIMULATOR_').Update(new_values)
        
    elif values['_INPUTCREATURESIMULATOR_'] == '':
        window.Element('_CREATURESSIMULATOR_').Update(get_creatures_list())