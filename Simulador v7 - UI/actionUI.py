import PySimpleGUI as sg
import os
from utilitiesUI import get_conditions_list, get_actions_list, save, load, damage_types
import copy

#ACTIONS
    
layout_action_statistics = [
    [sg.VPush()],
    [sg.Text("Name", size=(8, 1)), sg.Input(size=(50, 1), key='_ACTIONNAME_', justification='left', enable_events=True)],
    [sg.Text("Action Speed", size=(12,1)), sg.Combo(['Action', 'Bonus Action', 'Free Action', 'Follow-Up'], size=(12, 1), key='_ACTIONSPEED_')],
    [sg.Text("Number of Targets", size=(16, 1)), sg.Input(size=(2, 1), key='_NUMTARGETS_', justification='left', enable_events=True),
    sg.Text("Target Type", size=(11, 1)), sg.Combo(['Self', 'Enemy', 'Ally'], size=(6, 1), key='_TARGETTYPE_')],
    [sg.Text("Hint: A Follow-Up action won't be used normally. It will only be used when defined as a follow-up on a creature's action editor.")],  
    [sg.VPush()],
]

layout_action_costs = [
    [sg.VPush()],
    [sg.Text("Resource Name", size=(16, 1)), sg.Input(size=(20, 1), key='_ACTIONRESOURCENAME_', justification='left', enable_events=True),
    sg.Text("Resource Cost", size=(16, 1)), sg.Input(size=(5, 1), key='_ACTIONRESOURCECOST_', justification='left', enable_events=True)],
    [sg.Button('Add Cost', use_ttk_buttons=True),sg.Button('Delete Cost', use_ttk_buttons=True)],
    [sg.Listbox(values=[], size=(50, 5), key='_ResourceCosts_')],
    [sg.VPush()],
]

layout_action_conditions_sidebar = [
    [sg.Text('Available Conditions')],
    [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTACTIONCONDITION_', enable_events=True)],
    [sg.Listbox(values=get_conditions_list(), size=(20, 30), key='_ACTIONCONDITIONSSIDEBAR_', enable_events=True)],
]

layout_action_effects_sidebar = [
    [sg.VerticalSeparator(), sg.Column(layout_action_conditions_sidebar)],
    [sg.Button('Add Selected', use_ttk_buttons=True, visible=False, key='_ADDCONDITION_')],
]

layout_action_effects_main = [
    [sg.Text("Action Type", size=(8, 1)), sg.Combo(['Attack Roll', 'Saving Throw', 'Auto Apply'], size=(12, 1), key='_ACTIONTYPE_', enable_events=True)],
    [sg.pin(sg.Text("Attack Bonus", size=(12, 1), key='_ATTACKONLY_', visible=False)), sg.pin(sg.Input(size=(2, 1), key='_ATTACKBONUS_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Text("Save DC", size=(8, 1), key='_SAVEONLYDC_', visible=False)), sg.pin(sg.Input(size=(2, 1), key='_SAVEDC_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Text("Save Type", size=(8, 1), key='_SAVEONLYTYPE_', visible=False)), sg.pin(sg.Combo(['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'], size=(5, 1), key='_SAVETYPE_', visible=False))],
    [sg.Text("Effect", size=(8, 1)), sg.Combo(['Damage', 'Healing', 'Apply Condition'], size=(12, 1), key='_EFFECT_', enable_events=True)],
    [sg.pin(sg.Text("Half on Save?", key='_HALFONSAVETEXT_', visible=False)), sg.pin(sg.Checkbox('', default=False, key='_HALFONSAVE_', visible=False))],
    [sg.pin(sg.Text("Damage (XdY+Z)", size=(13, 1), key='_DAMAGEONLY_', visible=False)), sg.pin(sg.Input(size=(10, 1), key='_DAMAGEROLL_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Text("Damage Type", size=(11, 1), key='_DAMAGEONLY_', visible=False)), sg.pin(sg.Combo(values=damage_types, key='_DAMAGETYPE_', enable_events=True, visible=False))],
    [sg.pin(sg.Button('Add Damage', use_ttk_buttons=True, visible=False, key='_ADDDAMAGE_')), sg.pin(sg.Button('Delete Damage', use_ttk_buttons=True, visible=False, key='_DELETEDAMAGE_'))],
    [sg.pin(sg.Listbox(values=[], size=(50, 5), key='_DamageList_', visible=False))],
    [sg.pin(sg.Text("Healing (XdY+Z)", size=(13, 1), key='_HEALINGONLY_', visible=False)), sg.pin(sg.Input(size=(10, 1), key='_HEALINGROLL_', justification='left', enable_events=True, visible=False))],
    [sg.pin(sg.Button('Remove Selected', use_ttk_buttons=True, visible=False, key='_DELETECONDITION_'))],
    [sg.pin(sg.Listbox(values=[], size=(50, 5), key='_ConditionList_', visible=False))],
    [sg.pin(sg.Text("Concentration", key='_CONDITIONONLY_', visible=False)), sg.pin(sg.Checkbox('', default=False, key='_CONCENTRATION_', visible=False))]
]

layout_action_effects = [
    [sg.Column(layout_action_effects_main),sg.Column(layout_action_effects_sidebar, key='_EFFECTSSIDEBAR_', visible=False)]
]

layout_action_followups = [
    [sg.Text("Follow-up Actions")],
    [sg.Button('Add Follow-up Action', use_ttk_buttons=True, visible=True, key='_ADDFOLLOWUPACTION_'), sg.Button('Delete Follow-up Action', use_ttk_buttons=True, visible=True, key='_DELETEFOLLOWUPACTION_')],
    [sg.Listbox(values=[], size=(50, 5), key='_FollowupActionList_')]
]
    
layout_action_stats = [
    [sg.TabGroup([[sg.Tab('Basics',layout_action_statistics),
    sg.Tab('Costs',layout_action_costs),
    sg.Tab('Effects',layout_action_effects),
    sg.Tab('Followups',layout_action_followups,visible=False)]])],
    
    [sg.Button('Save', size=(10, 1), pad=((20, 0), 0), use_ttk_buttons=True, key='Save Action'),
    sg.Button('Load', size=(10, 1), use_ttk_buttons=True, key='Load Action')]
]

layout_actions_sidebar = [
    [sg.Text('Actions')],
    [sg.Input(do_not_clear=True, size=(20,1), key='_INPUTACTION_', enable_events=True)],
    [sg.Listbox(values=get_actions_list(), size=(20, 30), key='_ACTIONS_', enable_events=True)],
    [sg.Button('Create New', use_ttk_buttons=True, key='Create New Action')]
]

layout_actions = [
    [sg.Column(layout_actions_sidebar, element_justification='c'), sg.VerticalSeparator(), sg.Column(layout_action_stats)]
]


base_action_data = {
    'Name': 'New Action',
    'Action Speed': 'Action',
    'Number of Targets': '1',
    'Target Type': 'Self',
    'Resource Cost': [],
    'Action Type': '',
    'Effect': '',
    'Attack Bonus': '',
    'Save DC': '',
    'Save Type': '',
    'Half On Save': True,
    'Damage': [],
    'Healing Roll': '',
    'Conditions': [],
    'Concentration': False,
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

def update_action(action_data,window):
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
    if 'Half On Save' in action_data: 
        if action_data['Half On Save'] == 'True':
            window['_HALFONSAVE_'].update(True)
        elif action_data['Half On Save'] == 'False':
            window['_HALFONSAVE_'].update(False)
        else: window['_HALFONSAVE_'].update(action_data['Half On Save'])
    if 'Damage' in action_data:
        window['_DamageList_'].update(action_data['Damage'])
    else:
        window['_DamageList_'].update([])
    window['_HEALINGROLL_'].update(action_data['Healing Roll'])
    window['_ConditionList_'].update(action_data['Conditions'])
    if 'Concentration' in action_data: 
        if action_data['Concentration'] == 'True':
            window['_CONCENTRATION_'].update(True)
        elif action_data['Concentration'] == 'False':
            window['_CONCENTRATION_'].update(False)
        else: window['_CONCENTRATION_'].update(action_data['Concentration'])
    window['_FollowupActionList_'].update(action_data['Follow Actions'])

def update_action_data(values,window):
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


#Action Events
def events(event,values,window):
    global action_data
    if event == '_ACTIONS_' and len(values['_ACTIONS_']):
        selected_action = values['_ACTIONS_']
        selected_action_name = selected_action[0]
        filename = os.path.join(os.getcwd(), 'Actions', f'{selected_action_name}.json')
        print(filename)
        if os.path.exists(filename):
            action_data = load(filename)
        else:
            action_data = base_action_data
        update_action(action_data,window)
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
        window['_EFFECTSSIDEBAR_'].update(visible=action_data['Effect'] == 'Apply Condition')
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
        window['_HALFONSAVETEXT_'].update(visible=(values['_ACTIONTYPE_'] == 'Saving Throw' and values['_EFFECT_'] == 'Damage'))
        window['_HALFONSAVE_'].update(visible=(values['_ACTIONTYPE_'] == 'Saving Throw' and values['_EFFECT_'] == 'Damage'))
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
        window['_EFFECTSSIDEBAR_'].update(visible=values['_EFFECT_'] == 'Apply Condition')
    
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
        action_data['Damage'] = window['_DamageList_'].get_list_values()
    
    elif event == '_ADDCONDITION_' and values['_ACTIONCONDITIONSSIDEBAR_']:
        selected_condition = values['_ACTIONCONDITIONSSIDEBAR_'][0]
        filename = os.path.join(os.getcwd(), 'Conditions', selected_condition + '.json')
        if filename:
            condition_data = load(filename)
            action_data['Conditions'].append(condition_data)
            window['_ConditionList_'].update(action_data['Conditions'])
    elif event == '_DELETECONDITION_' and values['_ConditionList_']:
        selected_condition = values['_ConditionList_'][0]
        condition_data = window['_ConditionList_'].get_list_values()
        condition_data.remove(selected_condition)
        window['_ConditionList_'].update(condition_data)
        action_data['Conditions'] = window['_ConditionList_'].get_list_values()
        
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
        action_data['Follow Actions'] = window['_FollowupActionList_'].get_list_values()
        
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
        action_data['Resource Cost'] = window['_ResourceCosts_'].get_list_values()
    
    elif event == 'Create New Action':
        action_data = copy.deepcopy(base_action_data)
        update_action(action_data,window)
    
    elif event == 'Save Action':
        print(values)
        update_action_data(values,window)

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
            update_action(action_data,window)
            sg.popup(f'Action data loaded from {filename}', title='Load Successful')
            
    elif event == '_ACTIONCONDITIONSSIDEBAR_':
        pass
    
    elif values['_INPUTACTION_'] != '' or values['_INPUTACTIONCONDITION_'] != '':
        search = values['_INPUTACTION_']
        new_values = [x for x in get_actions_list() if search.lower() in x.lower()]
        window.Element('_ACTIONS_').Update(new_values)
        search = values['_INPUTACTIONCONDITION_']
        new_values = [x for x in get_conditions_list() if search.lower() in x.lower()]
        window.Element('_ACTIONCONDITIONSSIDEBAR_').Update(new_values)
        
    else:
        window.Element('_ACTIONS_').Update(get_actions_list())
        window.Element('_ACTIONCONDITIONSSIDEBAR_').Update(get_conditions_list())