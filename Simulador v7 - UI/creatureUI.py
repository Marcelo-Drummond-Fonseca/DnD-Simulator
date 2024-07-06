import PySimpleGUI as sg
import os
from utilitiesUI import get_creatures_list, get_creature_actions_list, get_actions_list, get_conditions_list, get_resources_list, save, load, damage_types, ttk_style
import copy

#CREATURES

layout_creature_statistics =[
    [sg.VPush()],
    [sg.Text("Name", size=(4, 1)), sg.Input(size=(50, 1), key='_CREATURENAME_', justification='left', enable_events=True),
    sg.Text('Party member?'), sg.Checkbox('', default=False, key='_PARTYMEMBER_', visible=True)],
    [sg.Text("HP", size=(2, 1)), sg.Input(size=(5, 1), key='_HP_', justification='left', enable_events=True),
    sg.Text("AC", size=(2, 1)), sg.DropDown(values=[str(i) for i in range(5,31)], size=(5, 1), key='_AC_'),
    sg.Text("Iniciative", size=(10, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(5, 1), key='_INICIATIVE_')],
    [sg.Text("LVL/CR"), sg.Input(size=(5, 1), key='_CR_', justification='left', enable_events=True),
    sg.Text("AI", size=(2,1)), sg.DropDown(values=['Damage','Tank','Support', 'Neutral'], size=(7,1), key='_AI_')],
    [sg.Text("Saving Throws")],
    [sg.Text("STR", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST1_'),
    sg.Text("DEX", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST2_'),
    sg.Text("CON", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST3_'),
    sg.Text("INT", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST4_'),
    sg.Text("WIS", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST5_'),
    sg.Text("CHA", size=(3, 1)), sg.DropDown(values=[str(i) for i in range(-3, 13)], size=(3, 1), key='_ST6_')],
    [sg.Text("Resistances/Immunities/Vulnerabilities"), sg.Button('Edit', use_ttk_buttons=True, key='_EDITRESISTANCE_')],
    [sg.Listbox(values=[], size=(50, 5), key='_ResistanceList_')],
    #[sg.DropDown(values=damage_types, key='_DAMAGETYPERESISTANCE_'), sg.Combo(values=['Resistance','Immunity','Vulnerability'], key='_RESISTANCETYPE_')],
    #[sg.Button('Add Resistance/Vulnerability/Immunity', use_ttk_buttons=True), sg.Button('Delete Resistance/Vulnerability/Immunity', use_ttk_buttons=True)],
    [sg.Column([
        [sg.Column([
            [sg.Text('Actions'), sg.Button('Edit', use_ttk_buttons=True, key='_EDITACTIONS_')],
            [sg.Listbox(values=[], size=(20, 10), key='_ActionList_', enable_events=True, visible=False)],
            [sg.Listbox(values=[], size=(25, 10), key='_ActionListNames_', enable_events=True)],
        ]),
        sg.Column([
            [sg.Text('Conditions'), sg.Button('Edit', use_ttk_buttons=True, key='_EDITCONDITIONS_')],
            [sg.Listbox(values=[], size=(20, 10), key='_CreatureConditionList_', enable_events=True, visible=False)],
            [sg.Listbox(values=[], size=(25, 10), key='_CreatureConditionListNames_', enable_events=True)],
        ]),
        sg.Column([
            [sg.Text("Resources"), sg.Button('Edit', use_ttk_buttons=True, key='_EDITRESOURCES_')],
            [sg.Listbox(values=[], size=(50, 5), key='_ResourcesList_', visible=False)],
            [sg.Listbox(values=[], size=(25, 10), key='_ResourcesListNames_')],
        ]),
        sg.Column([
            [sg.Text("Combos"), sg.Button('Edit', use_ttk_buttons=True, key='_EDITCOMBOS_')],
            [sg.Listbox(values=[], size=(25, 10), key='_ComboList_')],
        ]),
        ],
    ])],
    
    
    
    [sg.Text("Tags", visible=False)],
    [sg.Input(size=(50, 1), key='_CREATURETAG_', visible=False)],
    [sg.Button('Add Creature Tag', use_ttk_buttons=True, visible=False), sg.Button('Delete Creature Tag', use_ttk_buttons=True, visible=False)],
    [sg.Listbox(values=[], size=(50, 5), key='_CreatureTagList_', visible=False)],
    [sg.VPush()],
]

#layout_creature_resources = [
#    [sg.VPush()],
#    [sg.Text("Resources")],
#    [sg.Text("Name", size=(4, 1)), sg.Input(size=(20, 1), key='_ResourceName_'), 
#    sg.Text("Number", size=(6, 1)), sg.Input(size=(5, 1), key='_ResourceNumber_'),
#    sg.Text("Type", size=(4, 1)), sg.Combo(['Short Rest', 'Long Rest', 'Start of Turn', 'Recharge X'], size=(15, 1), key='_ResourceType_')],
#    [sg.Button('Add Resource', use_ttk_buttons=True), sg.Button('Delete Resource', use_ttk_buttons=True)],
#    [sg.Listbox(values=[], size=(50, 5), key='_ResourcesList_')],
#    [sg.VPush()],
#]

#layout_creature_combos = [
#    [sg.VPush()],
#    [sg.Text("Combos")],
#    [sg.Input(size=(30,1), key='_COMBONAME_', justification='left', enable_events=True)],
#    [sg.Button('Add Combo', use_ttk_buttons=True), sg.Button('Delete Combo', use_ttk_buttons=True)],
#    [sg.Listbox(values=[], size=(50, 20), key='_ComboList_')],
#    [sg.Text("Hint: For creatures that use multiple actions per turn, such as multiattack enemies or extra attack on player characters.\nFormat the combo with the name of each action separated by commas with no spaces. For example, 'Longsword,Longsword'.")], 
#    [sg.VPush()],
#]

#layout_creature_actions_editor = [
#    [sg.Text("Name", size=(8, 1)), sg.Input(size=(50, 1), key='_CREATUREACTIONNAME_', justification='left', enable_events=True)],
#    [sg.pin(sg.Text("Attack Bonus", size=(12, 1), key='_CREATUREACTIONATTACKONLY_', visible=False)), sg.pin(sg.Input(size=(2, 1), key='_CREATUREACTIONATTACKBONUS_', justification='left', enable_events=True, visible=False))],
#    [sg.pin(sg.Text("Save DC", size=(8, 1), key='_CREATUREACTIONSAVEONLYDC_', visible=False)), sg.pin(sg.Input(size=(2, 1), key='_CREATUREACTIONSAVEDC_', justification='left', enable_events=True, visible=False))],
#    [sg.pin(sg.Text("Save Type", size=(8, 1), key='_CREATUREACTIONSAVEONLYTYPE_', visible=False)), sg.pin(sg.Combo(['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'], size=(5, 1), key='_CREATUREACTIONSAVETYPE_', visible=False))],
#    [sg.pin(sg.Text("Damage (XdY+Z)", size=(13, 1), key='_CREATUREACTIONDAMAGEONLYDAMAGE_', visible=False)), sg.pin(sg.Input(size=(10, 1), key='_CREATUREACTIONDAMAGEROLL_', justification='left', enable_events=True, visible=False))],
#    [sg.pin(sg.Text("Damage Type", size=(11, 1), key='_CREATUREACTIONDAMAGEONLYTYPE_', visible=False)), sg.pin(sg.Combo(values=damage_types, key='_CREATUREACTIONDAMAGETYPE_', enable_events=True, visible=False))],
#    [sg.pin(sg.Button('Add Damage', use_ttk_buttons=True, visible=False, key='_CREATUREACTIONADDDAMAGE_')), sg.pin(sg.Button('Delete Damage', use_ttk_buttons=True, visible=False, key='_CREATUREACTIONDELETEDAMAGE_'))],
#    [sg.pin(sg.Listbox(values=[], size=(50, 5), key='_CreatureActionDamageList_', visible=False))],
#    [sg.pin(sg.Text("Healing (XdY+Z)", size=(13, 1), key='_CREATUREACTIONHEALINGONLY_', visible=False)), sg.pin(sg.Input(size=(10, 1), key='_CREATUREACTIONHEALINGROLL_', justification='left', enable_events=True, visible=False))],
#    [sg.pin(sg.Text("Follow-up Action: ", key='_CREATUREACTIONFOLLOWUPTEXT_', visible=True)), sg.pin(sg.Input(size=(15,1), key='_CREATUREACTIONFOLLOWUP_', enable_events=True, visible=True))],
#    [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Creature Action')],
#    [sg.Text("Hint: Editing actions here will affect only the selected creature's version of the action.")],   
#    [sg.Text("Hint: A Follow-up Action named here will attempt to apply if this action is successful.\nThe follow-up action must also be included in the creature's actions.\nUsed for things such as Divine Smite or Stunning Strike.")],   
#]

#layout_creature_actions_sidebar = [
#    [sg.Text('Creature Actions')],
#    [sg.Listbox(values=[], size=(20, 30), key='_ActionList_', enable_events=True)],
#    [sg.Button('Remove Selected', use_ttk_buttons=True, key='Delete Action')]
#]
#
#layout_creature_all_actions_sidebar = [
#    [sg.Text('Available Actions')],
#    [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTCREATUREACTION_', enable_events=True)],
#    [sg.Listbox(values=get_actions_list(), size=(20, 30), key='_CREATUREACTIONSSIDEBAR_', enable_events=True)],
#    [sg.Button('Add Selected', use_ttk_buttons=True, key='Add Action')],
#]
#
#
#
#layout_creature_actions = [
#    [sg.VPush()],
#    [sg.Column(layout_creature_actions_sidebar, element_justification='c'), sg.VerticalSeparator(), sg.Column(layout_creature_actions_editor), sg.VerticalSeparator(), sg.Column(layout_creature_all_actions_sidebar)],
#    [sg.VPush()],
#]
#
#layout_creature_conditions_sidebar = [
#    [sg.Text('Available Conditions')],
#    [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTCREATURECONDITION_', enable_events=True)],
#    [sg.Listbox(values=get_conditions_list(), size=(20, 30), key='_CREATURECONDITIONSSIDEBAR_', enable_events=True)],
#    [sg.Button('Add Selected', use_ttk_buttons=True, key='_ADDCREATURECONDITION_')],
#]
#
#layout_creature_conditions_main = [
#    [sg.Text("Creature conditions")],
#    [sg.Button('Remove Selected', use_ttk_buttons=True, key='_DELETECREATURECONDITION_')],
#    [sg.Listbox(values=[], size=(50, 5), key='_CreatureConditionList_')]
#]
#
#layout_creature_conditions = [
#    [sg.VPush()],
#    [sg.Column(layout_creature_conditions_main),sg.VerticalSeparator(),sg.Column(layout_creature_conditions_sidebar)],
#    [sg.VPush()],
#]

layout_creature_stats = [
    [sg.Column(layout_creature_statistics)],    
    [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Creature'),
    sg.Button('Load', size=(10, 1), use_ttk_buttons=True, key='Load Creature')]
]

layout_creatures_sidebar = [
    [sg.Text('Creatures')],
    [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTCREATURE_', enable_events=True)],
    [sg.Listbox(values=get_creatures_list(False), size=(20, 30), key='_CREATURES_', enable_events=True)],
    [sg.Button('Create New', use_ttk_buttons=True, key='Create New Creature')],
    [sg.Text('Party Only'),sg.Checkbox('', default=False, key='_PARTYONLY_', visible=True, enable_events=True)],
]

layout_creatures = [
    [sg.Column(layout_creatures_sidebar, element_justification='c'), sg.VerticalSeparator(), sg.Column(layout_creature_stats)]
]

#Popup Layouts

def make_edit_resistances(creature_data):
    layout_edit_resistances = [
        [sg.Text("Resistances/Immunities/Vulnerabilities")],
        [sg.DropDown(values=damage_types, key='_DAMAGETYPERESISTANCE_'), sg.Combo(values=['Resistance','Immunity','Vulnerability'], key='_RESISTANCETYPE_')],
        [sg.Button('Add Resistance/Vulnerability/Immunity', use_ttk_buttons=True), sg.Button('Delete Resistance/Vulnerability/Immunity', use_ttk_buttons=True)],
        [sg.Listbox(values=creature_data['Resistances'], size=(50, 5), key='_ResistanceListTemp_')],
        [sg.Button('Save Changes', use_ttk_buttons=True, key='_SAVERESISTANCEEDIT_')]
    ]
    return sg.Window('Edit Resistances',layout_edit_resistances,ttk_theme=ttk_style,modal=True,finalize=True)

def make_edit_actions(creature_data):
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
        [sg.pin(sg.Text("Follow-up Action: ", key='_CREATUREACTIONFOLLOWUPTEXT_', visible=True)), sg.pin(sg.DropDown(get_creature_actions_list(creature_data), size=(15,1), key='_CREATUREACTIONFOLLOWUP_', enable_events=True, visible=True))],
        [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Creature Action')],
        [sg.Text("Hint: Editing actions here will affect only the selected creature's version of the action.")],   
        [sg.Text("Hint: A Follow-up Action named here will attempt to apply if this action is successful.\nThe follow-up action must also be included in the creature's actions.\nUsed for things such as Divine Smite or Stunning Strike.")],   
    ]

    layout_creature_actions_sidebar = [
        [sg.Text('Creature Actions')],
        [sg.Listbox(values=creature_data['Actions'], key='_ActionListTemp_', enable_events=True, visible=False)],
        [sg.Listbox(values=[f'{action["Name"]} ({action["Action Speed"]})' for action in creature_data['Actions']], size=(30, 30), key='_ActionListTempNames_', enable_events=True)],
        [sg.Button('Remove Selected', use_ttk_buttons=True, key='Delete Action')]
    ]

    layout_creature_all_actions_sidebar = [
        [sg.Text('Available Actions')],
        [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTCREATUREACTION_', enable_events=True)],
        [sg.Listbox(values=get_actions_list(), size=(20, 30), key='_CREATUREACTIONSSIDEBAR_', enable_events=True)],
        [sg.Button('Add Selected', use_ttk_buttons=True, key='Add Action')],
    ]
    
    layout_creature_actions = [
        [sg.VPush()],
        [sg.Column(layout_creature_actions_sidebar, element_justification='c'), sg.VerticalSeparator(), sg.Column(layout_creature_actions_editor), sg.VerticalSeparator(), sg.Column(layout_creature_all_actions_sidebar)],
        [sg.VPush()],
    ]
    
    return sg.Window('Edit Actions',layout_creature_actions,ttk_theme=ttk_style,modal=True,finalize=True)

def make_edit_conditions(creature_data):
    layout_creature_conditions_sidebar = [
        [sg.Text('Available Conditions')],
        [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTCREATURECONDITION_', enable_events=True)],
        [sg.Listbox(values=get_conditions_list(), size=(20, 30), key='_CREATURECONDITIONSSIDEBAR_', enable_events=True)],
        [sg.Button('Add Selected', use_ttk_buttons=True, key='_ADDCREATURECONDITION_')],
    ]

    layout_creature_conditions_main = [
        [sg.Text("Creature conditions")],
        [sg.Button('Remove Selected', use_ttk_buttons=True, key='_DELETECREATURECONDITION_')],
        [sg.Listbox(values=creature_data['Conditions'], size=(50, 5), key='_CreatureConditionListTemp_', visible=False)],
        [sg.Listbox(values=[condition['Name'] for condition in creature_data['Conditions']], size=(50, 5), key='_CreatureConditionListTempNames_')],
        [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Creature Condition')],
    ]

    layout_creature_conditions = [
        [sg.VPush()],
        [sg.Column(layout_creature_conditions_main),sg.VerticalSeparator(),sg.Column(layout_creature_conditions_sidebar)],
        [sg.VPush()],
    ]
    
    return sg.Window('Edit Conditions',layout_creature_conditions,ttk_theme=ttk_style,modal=True,finalize=True)

def make_edit_resources(creature_data):
    layout_creature_resources = [
        [sg.VPush()],
        [sg.Text("Resources")],
        [sg.Text("Name", size=(4, 1)), sg.DropDown(get_resources_list(), size=(20, 1), key='_ResourceName_'), 
        sg.Text("Number", size=(6, 1)), sg.Input(size=(5, 1), key='_ResourceNumber_'),
        sg.Text("Type", size=(4, 1)), sg.Combo(['Short Rest', 'Long Rest', 'Start of Turn', 'Recharge X'], size=(15, 1), key='_ResourceType_')],
        [sg.Button('Add Resource', use_ttk_buttons=True), sg.Button('Delete Resource', use_ttk_buttons=True)],
        [sg.Listbox(values=creature_data['Resources'], size=(50, 5), key='_ResourcesListTemp_', visible=False)],
        [sg.Listbox(values=[f'{resource["Name"]} ({resource["Number"]} per {resource["Type"]})' for resource in creature_data['Resources']], size=(50, 5), key='_ResourcesListTempNames_')],
        [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Creature Resource')],
        [sg.VPush()],
    ]
    
    return sg.Window('Edit Resources',layout_creature_resources,ttk_theme=ttk_style,modal=True,finalize=True)

def make_edit_combos(creature_data):
    layout_creature_combos = [
        [sg.VPush()],
        [sg.Text("Actions")],
        [sg.DropDown(get_creature_actions_list(creature_data), key='_ACTIONSFORCOMBO_')],
        [sg.Button('Add Action to Combo', use_ttk_buttons=True), sg.Button('Remove Action from Combo', use_ttk_buttons=True)],
        [sg.Text("Combos")],
        [sg.Input(size=(60,1), key='_COMBONAME_', justification='left', enable_events=True, disabled=True)],
        [sg.Button('Add Combo', use_ttk_buttons=True), sg.Button('Delete Combo', use_ttk_buttons=True)],
        [sg.Listbox(values=creature_data['Combos'], size=(50, 20), key='_ComboListTemp_')],
        [sg.Text("Hint: For creatures that use multiple actions per turn, such as multiattack enemies or extra attack on player characters.\nFormat the combo with the name of each action separated by commas with no spaces. For example, 'Longsword,Longsword'.")], 
        [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Creature Combo')],
        [sg.VPush()],
    ]
    
    return sg.Window('Edit Combos',layout_creature_combos,ttk_theme=ttk_style,modal=True,finalize=True)

#CREATURE DATA
base_creature_data = {
    'Name': 'New Creature',
    'HP': '1',
    'AC': '10',
    'Iniciative': '0',
    'LVL/CR': '1',
    'Saving Throws': ['0', '0', '0', '0', '0', '0'],
    'Resources': [],
    'Actions': [],
    'Conditions': [],
    'Combos': [],
    'Resistances': [],
    'AI': 'Damage',
    'Tags': [],
    'Party': False,
}

creature_data = {
    'Name': None,
    'HP': None,
    'AC': None,
    'Iniciative': None,
    'LVL/CR': None,
    'Saving Throws': [None, None, None, None, None, None],
    'Resources': [],
    'Actions': [],
    'Conditions': [],
    'Combos': [],
    'Resistances': [],
    'AI': None,
    'Tags': [],
    'Party': False,
}

def update_creature(creature_data,window):
    window['_CREATURENAME_'].update(creature_data['Name'])
    window['_HP_'].update(creature_data['HP'])
    window['_AC_'].update(creature_data['AC'])
    window['_INICIATIVE_'].update(creature_data['Iniciative'])
    for i in range(1, 7):
        window[f'_ST{i}_'].update(creature_data['Saving Throws'][i-1])
    window['_ResourcesList_'].update(creature_data['Resources'])
    window['_ResourcesListNames_'].update([f'{resource["Name"]} ({resource["Number"]} per {resource["Type"]})' for resource in creature_data['Resources']])
    window['_ActionList_'].update(creature_data['Actions'])
    window['_ActionListNames_'].update([f'{action["Name"]} ({action["Action Speed"]})' for action in creature_data['Actions']])
    if 'Conditions' in creature_data: window['_CreatureConditionList_'].update(creature_data['Conditions'])
    else: creature_data['Conditions'] = []
    window['_ComboList_'].update(creature_data['Combos'])
    window['_ResistanceList_'].update(creature_data['Resistances'])
    if 'LVL/CR' in creature_data: window['_CR_'].update(creature_data['LVL/CR'])
    if 'AI' in creature_data: window['_AI_'].update(creature_data['AI'])
    if 'Tags' in creature_data: window['_CreatureTagList_'].update(creature_data['Tags'])
    if 'Party' in creature_data: window['_PARTYMEMBER_'].update(creature_data['Party'])
    else: window['_PARTYMEMBER_'].update(False)

def update_creature_data(values,window):
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
    creature_data['LVL/CR'] = values['_CR_']
    creature_data['AI'] = values['_AI_']
    creature_data['Tags'] = window['_CreatureTagList_'].get_list_values()
    creature_data['Party'] = values['_PARTYMEMBER_']
    
def update_creature_action(creature_data,action,window):
    window['_CREATUREACTIONNAME_'].update(action['Name'])
    window['_CREATUREACTIONATTACKBONUS_'].update(action['Attack Bonus'])
    window['_CREATUREACTIONSAVEDC_'].update(action['Save DC'])
    window['_CREATUREACTIONSAVETYPE_'].update(action['Save Type'])
    if 'Damage' in action: window['_CreatureActionDamageList_'].update(action['Damage'])
    window['_CREATUREACTIONHEALINGROLL_'].update(action['Healing Roll'])
    window['_CREATUREACTIONFOLLOWUP_'].update(action['Follow Action'], values=get_creature_actions_list(creature_data,action))
    
def update_creature_action_data(values,window):
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

#CREATURE EVENTS


def events(event,values,window,main_window,secondary_window):
    global creature_data
    global opened_creature_action
    
    if event == '_CREATURES_' and len(values['_CREATURES_']):
        selected_creature = values['_CREATURES_']
        selected_creature_name = selected_creature[0]
        filename = os.path.join(os.getcwd(), 'Creatures', f'{selected_creature_name}.json')
        if os.path.exists(filename):
            creature_data = load(filename)
        else:
            creature_data = base_creature_data
        update_creature(creature_data,window)
    
    elif event == '_PARTYONLY_':
        window.Element('_CREATURES_').Update(get_creatures_list(values['_PARTYONLY_']))
        
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
    
    elif event == '_EDITRESOURCES_':
        secondary_window = make_edit_resources(creature_data)
    elif event == 'Add Resource':
        name = values['_ResourceName_']
        number = values['_ResourceNumber_']
        rtype = values['_ResourceType_']
        resource_data = window['_ResourcesListTemp_'].get_list_values()
        resource_data.append({'Name': name, 'Number': number, 'Type': rtype})
        window['_ResourcesListTemp_'].update(resource_data)
        window['_ResourcesListTempNames_'].update([f'{resource["Name"]} ({resource["Number"]} per {resource["Type"]})' for resource in window['_ResourcesListTemp_'].get_list_values()])
    elif event == 'Delete Resource' and values['_ResourcesListTempNames_']:
        selected_resource = window['_ResourcesListTemp_'].get_list_values()[window['_ResourcesListTempNames_'].get_indexes()[0]]
        resource_data = window['_ResourcesListTemp_'].get_list_values()
        resource_data.remove(selected_resource)
        window['_ResourcesListTemp_'].update(resource_data)
        window['_ResourcesListTempNames_'].update([f'{resource["Name"]} ({resource["Number"]} per {resource["Type"]})' for resource in window['_ResourcesListTemp_'].get_list_values()])
        #creature_data['Resources'] = window['_ResourcesList_'].get_list_values()
    elif event == 'Save Creature Resource':
        main_window['_ResourcesList_'].update(window['_ResourcesListTemp_'].get_list_values())
        creature_data['Resources'] = main_window['_ResourcesList_'].get_list_values()
        main_window['_ResourcesListNames_'].update(window['_ResourcesListTempNames_'].get_list_values())
        window.close()
    
    elif event == '_EDITACTIONS_':
        secondary_window = make_edit_actions(creature_data)
    
    elif event == '_ActionListTempNames_' and len(values['_ActionListTempNames_']):
        selected_action = window['_ActionListTemp_'].get_list_values()[window['_ActionListTempNames_'].get_indexes()[0]]
        opened_creature_action = selected_action
        update_creature_action(creature_data,selected_action,window)
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
        update_creature_action_data(values,window)
        creature_data['Actions'] = window['_ActionListTemp_'].get_list_values()

        # Show a file save dialog and get the chosen filename
        #filename = sg.popup_get_file('Save Creature Data', save_as=True, default_extension='.json', file_types=(('JSON Files', '*.json'),))
        filename = os.path.join(os.getcwd(),'Creatures')
        filename = os.path.join(filename,f"{creature_data['Name']}.json")
        
        if filename:
            save(filename, creature_data)
            sg.popup(f'Creature data saved to {filename}', title='Save Successful')
        
        window['_ActionListTemp_'].update(creature_data['Actions'])
        window['_ActionListTempNames_'].update([f'{action["Name"]} ({action["Action Speed"]})' for action in creature_data['Actions']])
        main_window['_ActionList_'].update(creature_data['Actions'])
        main_window['_ActionListNames_'].update([f'{action["Name"]} ({action["Action Speed"]})' for action in creature_data['Actions']])
        
    
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
    
    
    
    elif event == 'Add Action' and values['_CREATUREACTIONSSIDEBAR_']:
        selected_action = values['_CREATUREACTIONSSIDEBAR_'][0]
        filename = os.path.join(os.getcwd(), 'Actions', selected_action + '.json')
        if filename:
            action_data = load(filename)
            #creature_data['Actions'].append(action_data)
            window['_ActionListTemp_'].update(window['_ActionListTemp_'].get_list_values().append(action_data))
            window['_ActionListTempNames_'].update([f'{action["Name"]} ({action["Action Speed"]})' for action in window['_ActionListTemp_'].get_list_values()])
    elif event == 'Delete Action' and values['_ActionListTempNames_']:
        selected_action = window['_ActionListTemp_'].get_list_values()[window['_ActionListTempNames_'].get_indexes()[0]]
        action_data = window['_ActionListTemp_'].get_list_values()
        action_data.remove(selected_action)
        window['_ActionListTemp_'].update(action_data)
        window['_ActionListTempNames_'].update([f'{action["Name"]} ({action["Action Speed"]})' for action in window['_ActionListTemp_'].get_list_values()])
        #creature_data['Actions'] = window['_ActionListTemp_'].get_list_values()
        
    
    elif event == '_EDITCONDITIONS_':
        secondary_window = make_edit_conditions(creature_data)
    elif event == '_ADDCREATURECONDITION_' and values['_CREATURECONDITIONSSIDEBAR_']:
        selected_condition = values['_CREATURECONDITIONSSIDEBAR_'][0]
        filename = os.path.join(os.getcwd(), 'Conditions', selected_condition + '.json')
        if filename:
            condition_data = load(filename)
            window['_CreatureConditionListTemp_'].update(window['_CreatureConditionListTemp_'].get_list_values().append(condition_data))
            window['_CreatureConditionListTempNames_'].update([condition['Name'] for condition in window['_CreatureConditionListTemp_'].get_list_values()])
    elif event == '_DELETECREATURECONDITION_' and values['_CreatureConditionListTempNames_']:
        selected_condition = window['_CreatureConditionListTemp_'].get_list_values()[window['_CreatureConditionListTempNames_'].get_indexes()[0]]
        condition_data = window['_CreatureConditionListTemp_'].get_list_values()
        condition_data.remove(selected_condition)
        window['_CreatureConditionListTemp_'].update(condition_data)
        window['_CreatureConditionListTempNames_'].update([condition['Name'] for condition in window['_CreatureConditionListTemp_'].get_list_values()])
        #creature_data['Conditions'] = window['_CreatureConditionList_'].get_list_values()
    elif event == 'Save Creature Condition':
        main_window['_CreatureConditionList_'].update(window['_CreatureConditionListTemp_'].get_list_values())
        creature_data['Conditions'] = main_window['_CreatureConditionList_'].get_list_values()
        main_window['_CreatureConditionListNames_'].update([condition['Name'] for condition in creature_data['Conditions']])
        window.close()
    
    elif event == '_EDITCOMBOS_':
        secondary_window = make_edit_combos(creature_data)
    
    elif event == 'Add Action to Combo' and values['_ACTIONSFORCOMBO_']:
        if values['_COMBONAME_']:
            window['_COMBONAME_'].update(value=values['_COMBONAME_'] + ',' + values['_ACTIONSFORCOMBO_'])
        else:
            window['_COMBONAME_'].update(value=values['_ACTIONSFORCOMBO_'])
    elif event == 'Remove Action from Combo':
        last_comma_index = values['_COMBONAME_'].rfind(',')
        if last_comma_index == -1:
            window['_COMBONAME_'].update(value='')
        else: 
            window['_COMBONAME_'].update(values['_COMBONAME_'][:last_comma_index])
    
    elif event == 'Add Combo':
        combo_data = window['_ComboListTemp_'].get_list_values()
        combo_data.append(values['_COMBONAME_'])
        window['_ComboListTemp_'].update(combo_data)
    elif event == 'Delete Combo' and values['_ComboListTemp_']:
        selected_combo = values['_ComboListTemp_'][0]
        combo_data = window['_ComboListTemp_'].get_list_values()
        combo_data.remove(selected_combo)
        window['_ComboListTemp_'].update(combo_data)
        #creature_data['Combos'] = window['_ComboList_'].get_list_values()
    elif event == 'Save Creature Combo':
        main_window['_ComboList_'].update(window['_ComboListTemp_'].get_list_values())
        creature_data['Combos'] = main_window['_ComboList_'].get_list_values()
        window.close()
    
    elif event == '_EDITRESISTANCE_':
        secondary_window = make_edit_resistances(creature_data)  
    elif event == 'Add Resistance/Vulnerability/Immunity':
        resistance_data = window['_ResistanceListTemp_'].get_list_values()
        resistance_data.append([values['_DAMAGETYPERESISTANCE_'], values['_RESISTANCETYPE_']])
        window['_ResistanceListTemp_'].update(resistance_data)
    elif event == 'Delete Resistance/Vulnerability/Immunity' and values['_ResistanceListTemp_']:
        selected_resistance = values['_ResistanceListTemp_'][0]
        resistance_data = window['_ResistanceListTemp_'].get_list_values()
        resistance_data.remove(selected_resistance)
        window['_ResistanceListTemp_'].update(resistance_data)
        #creature_data['Resistances'] = window['_ResistanceListTemp_'].get_list_values()
    elif event == '_SAVERESISTANCEEDIT_':
        main_window['_ResistanceList_'].update(window['_ResistanceListTemp_'].get_list_values())
        creature_data['Resistances'] = main_window['_ResistanceList_'].get_list_values()
        window.close()
        
    
    elif event == 'Create New Creature':
        creature_data = copy.deepcopy(base_creature_data)
        update_creature(creature_data,window)
    
    elif event == 'Save Creature':# Update creature_data with input values
        update_creature_data(values,window)

        # Show a file save dialog and get the chosen filename
        #filename = sg.popup_get_file('Save Creature Data', save_as=True, default_extension='.json', file_types=(('JSON Files', '*.json'),))
        filename = os.path.join(os.getcwd(),'Creatures')
        filename = os.path.join(filename,f"{creature_data['Name']}.json")
        
        if filename:
            save(filename, creature_data)
            sg.popup(f'Creature data saved to {filename}', title='Save Successful')      
            window.Element('_CREATURES_').Update(get_creatures_list(values['_PARTYONLY_']))
        
        #Party stuff
        filename = os.path.join(os.getcwd(),'Creatures\Party')
        filename = os.path.join(filename,f"{creature_data['Name']}.json")
        
        if creature_data['Party']:
            if filename:
                save(filename, creature_data)
                
        elif os.path.exists(filename):
            os.remove(filename)
        
    elif event == 'Load Creature':
        # Show a file open dialog and get the chosen filename
        filename = sg.popup_get_file('Load Creature Data', file_types=(('JSON Files', '*.json'),))
        
        if filename:
            creature_data = load(filename)
            update_creature(creature_data,window)
            sg.popup(f'Creature data loaded from {filename}', title='Load Successful')
    
    elif event == '_CREATUREACTIONSSIDEBAR_' or event == '_CREATURECONDITIONSSIDEBAR_':
        pass
    
    elif (event == '_INPUTCREATURE_' and values['_INPUTCREATURE_'] != '') or (event == '_INPUTCREATUREACTION_' and values['_INPUTCREATUREACTION_'] != '') or (event == '_INPUTCREATURECONDITION_' and values['_INPUTCREATURECONDITION_'] != ''):
        search = values['_INPUTCREATURE_']
        new_values = [x for x in get_creatures_list(values['_PARTYONLY_']) if search.lower() in x.lower()]
        window.Element('_CREATURES_').Update(new_values)
        search = values['_INPUTCREATUREACTION_']
        new_values = [x for x in get_actions_list() if search.lower() in x.lower()]
        window.Element('_CREATUREACTIONSSIDEBAR_').Update(new_values)
        search = values['_INPUTCREATURECONDITION_']
        new_values = [x for x in get_conditions_list() if search.lower() in x.lower()]
        window.Element('_CREATURECONDITIONSSIDEBAR_').Update(new_values)
        
    elif (event == '_INPUTCREATURE_' and values['_INPUTCREATURE_'] == ''):
        window.Element('_CREATURES_').Update(get_creatures_list(values['_PARTYONLY_']))
        
    elif (event == '_INPUTCREATUREACTION_' and values['_INPUTCREATUREACTION_'] == ''):
        window.Element('_CREATUREACTIONSSIDEBAR_').Update(get_actions_list())
        
    elif (event == '_INPUTCREATURECONDITION_' and values['_INPUTCREATURECONDITION_'] != ''):    
        window.Element('_CREATURECONDITIONSSIDEBAR_').Update(get_conditions_list())
        