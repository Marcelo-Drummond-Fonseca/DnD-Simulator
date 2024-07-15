import re
from creature import Creature
from action import Action, Attack_Roll, Auto_Apply, Saving_Throw, Damage, Healing, Apply_Condition
from conditions import Condition, Condition_Effect, Modified_Attack, Modified_Defense, Modified_Economy, Effect_Over_Time



saves_dict = {
    'STR': 0,
    'DEX': 1,
    'CON': 2,
    'INT': 3,
    'WIS': 4,
    'CHA': 5
}
damage_multiplier = {'Resistance': 0.5, 'Immunity': 0, 'Vulnerability': 2}

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
    if condition['Attack Modifier'] or condition['Attack Advantage'] or condition['Damage Modifier'] or condition['Crits On'] != 20 or condition['Extra Damage Roll']:
        if condition['Attack Advantage'] == 'Advantage': advantage = 1
        elif condition['Attack Advantage'] == 'Disadvantage': advantage = -1
        else: advantage = 0
        extra_damage = []
        if condition['Extra Damage Roll'] and condition['Extra Damage Type']:
            extra_damage = format_roll(condition['Extra Damage Roll'])
            extra_damage.append(condition['Extra Damage Type'])
        effectslist.append(Modified_Attack(int(condition['Attack Modifier']), int(condition['Damage Modifier']), advantage, extra_damage = extra_damage, crit_threshold = int(condition['Crits On'])))
    if condition['AC Modifier'] or condition['Defense Advantage'] or condition['Saves Modifier'] or condition['Saves Advantage'] or condition['Resistances'] or condition['Auto Crit'] == "True" or condition['Evasion']:
        if condition['Defense Advantage'] == 'Advantage': advantage = 1
        elif condition['Defense Advantage'] == 'Disadvantage': advantage = -1
        else: advantage = 0
        saves_advantage = [1 if adv == "Advantage" else -1 if adv == "Disadvantage" else 0 for adv in condition['Saves Advantage']]
        resistances = {}
        for resistance in condition['Resistances']:
            resistances[resistance[0]] = damage_multiplier[resistance[1]]
        if not 'Evasion' in condition:
            condition['Evasion'] = [False,False,False,False,False,False]
        elif isinstance(condition['Evasion'][0], str):
            for i in range (6):
                condition['Evasion'][i] = condition['Evasion'][i] == 'True'
        guaranteed_crit = False
        if 'Auto Crit' in condition:
            if isinstance(condition['Auto Crit'], bool):
                paired = condition['Auto Crit']
            else:
                if condition['Auto Crit'] == 'True': paired = True
        effectslist.append(Modified_Defense(int(condition['AC Modifier']), advantage, list(map(int, condition['Saves Modifier'])), saves_advantage, resistances, auto_crit = guaranteed_crit, evasion=condition['Evasion']))
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
        if isinstance(condition['Paired Condition'], bool):
            paired = condition['Paired Condition']
        else:
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
            is_concentration = False
            if isinstance(action['Concentration'], bool):
                is_concentration = action['Concentration']
            else:
                is_concentration = action['Concentration'] == "True"
            effect = Apply_Condition(formatted_condition, is_concentration)
    if action['Action Type'] == 'Attack Roll':
        attempt = Attack_Roll(int(action['Attack Bonus']), effect)
    elif action['Action Type'] == 'Saving Throw':
        half_on_save = True
        if action['Effect'] == 'Damage':
            if isinstance(action['Half On Save'], bool):
                half_on_save = action['Half On Save']
            else:
                half_on_save = action['Half On Save'] == "True"
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
