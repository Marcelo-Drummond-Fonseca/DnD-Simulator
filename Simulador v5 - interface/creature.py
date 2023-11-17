from random import choice
from diceroller import d20roll, diceroll
from math import floor

class Creature:

    def __init__(self, name, max_hit_points, armor_class, saving_throws, iniciative):
        self.name = name
        self.MHP = max_hit_points
        self.HP = self.MHP
        self.AC = armor_class
        self.AC_advantage = 0
        self.AC_disadvantage = 0
        self.saving_throws = saving_throws
        self.save_advantage = [0,0,0,0,0,0]
        self.save_disadvantage = [0,0,0,0,0,0]
        self.iniciative = iniciative
        self.actions = []
        self.bonus_actions = []
        self.free_actions = []
        self.combos = []
        self.action_number = 1
        self.bonus_action_number = 1
        self.reaction_number = 1
        self.damage_type_multipliers = {}
        self.damage_type_reductions = {}
        self.max_resources = {}
        self.current_resources = {}
        self.rest_resources = {}
        self.recharge_resources = {}
        self.concentration = False
        self.conditions = []
        self.applied_conditions = {
            "Concentration": [],
            "Non-Concentration": []
        }
        simulator = None
        team = 0
        
    def add_action(self, action):
        self.actions.append(action)
        
    def add_bonus_action(self, action):
        self.bonus_actions.append(action)
    
    def add_free_action(self, action):
        self.free_actions.append(action)
        
    def add_combo(self, combo):
        new_combo = []
        for combo_piece in combo:
            combo_index = None
            for index, action in enumerate(self.actions):
                if action.name == combo_piece:
                    combo_index = index
            if combo_index is not None:
                new_combo.append(combo_index)
        self.combos.append(new_combo)
                    
    
    def add_damage_type_multiplier(self, damage_type, multiplier):
        self.damage_type_multipliers[damage_type] = multiplier
        
    def add_resource(self, resource_type, resource_amount, regain_type, recharge_number = None):
        self.max_resources[resource_type] = resource_amount
        self.current_resources[resource_type] = resource_amount
        if regain_type == 'Short Rest':
            self.rest_resources[resource_type] = 'Short Rest'
        elif regain_type == 'Long Rest':
            self.rest_resources[resource_type] = 'Long Rest'
        elif regain_type == 'Recharge':
            self.recharge_resources[resource_type] = recharge_number
    
    def full_restore(self):
        self.HP = self.MHP
        for resource_type, resource_amount in self.max_resources.items():
            self.current_resources[resource_type] = self.max_resources[resource_type]
        for condition in self.conditions:
            condition.remove_condition()
    
    def add_simulator(self, simulator, team):
        self.simulator = simulator
        self.team = team
    
    def add_applied_condition(self, condition, concentration):
        if concentration:
            self.applied_conditions["Concentration"].append(condition)
        else:
            self.applied_conditions["Non-Concentration"].append(condition)
    
    def remove_applied_condition(self,condition):
        if condition in self.applied_conditions["Concentration"]:
            self.applied_conditions["Concentration"].remove(condition)
        elif condition in self.applied_conditions["Non-Concentration"]:
            self.applied_conditions["Non-Concentration"].remove(condition)
    
    def add_condition(self, condition):
        self.conditions.append(condition)
        print(self.name, "ganhou condição:", condition.name)
    
    def remove_condition(self, condition):
        self.conditions.remove(condition)
        print(self.name, "perdeu condição:", condition.name)
    
    def choose_combo(self):
        possible_actions = []
        for combo in self.combos:
            actions = [self.actions[i] for i in combo]
            possible = True
            necessary_resources = {}
            for action in actions:
                if action.resource_cost:
                    if action.resource_cost[0] in necessary_resources:
                        necessary_resources[action.resource_cost[0]] += action.resource_cost[1]
                    else:
                        necessary_resources[action.resource_cost[0]] = action.resource_cost[1]
            for resource_type, resource_amount in necessary_resources.items():
                if self.current_resources[resource_type] < resource_amount:
                    possible = False
            if possible:
                possible_actions.append(actions)
        actions = choice(possible_actions)
        for action in actions:
            #target = choice(self.simulator.get_enemy_team(self.team))
            targets = action.get_targets(self)
            print(self.name, 'usa', action.name, 'contra', *(getattr(creature, "name") for creature in targets))
            if action.resource_cost:
                self.current_resources[action.resource_cost[0]] -= action.resource_cost[1]
            action.act(targets, self)
        
    
    def choose_single_action(self, action_type):
        possible_actions = []
        for action in action_type:
            possible = True
            necessary_resources = {}
            if action.resource_cost:
                if action.resource_cost[0] in necessary_resources:
                    necessary_resources[action.resource_cost[0]] += action.resource_cost[1]
                else:
                    necessary_resources[action.resource_cost[0]] = action.resource_cost[1]
            for resource_type, resource_amount in necessary_resources.items():
                if self.current_resources[resource_type] < resource_amount:
                    possible = False
            if possible:
                possible_actions.append(action)
        if possible_actions:
            action = choice(possible_actions)
            #target = choice(self.simulator.get_enemy_team(self.team))
            targets = action.get_targets(self)
            print(self.name, 'usa', action.name, 'contra', *(getattr(creature, "name") for creature in targets))
            if action.resource_cost:
                self.current_resources[action.resource_cost[0]] -= action.resource_cost[1]
            action.act(targets, self)
        
    
    def start_of_turn(self):
        print('\nTurno de:', self.name)
        for condition in self.conditions:
            condition.notify_SoT(isCaster = False)
        for condition in self.applied_conditions['Concentration']:
            condition.notify_SoT(isCaster = True)
        for condition in self.applied_conditions['Non-Concentration']:
            condition.notify_SoT(isCaster = True)
        self.take_turn()
    
    def take_turn(self):
        #Recharge
        for resource_type, recharge in self.recharge_resources.items():
            if recharge <= diceroll(1,6,0):
                self.current_resources[resource_type] = self.max_resources[resource_type]
                print(self.name,'Recarrega seu',resource_type)
        
        
        #Filtrar Free actions por recursos
        self.choose_single_action(self.free_actions)
        for i in range(self.bonus_action_number):
            #Filtrar ações bonus por recursos
            self.choose_single_action(self.bonus_actions)
        for i in range(self.action_number):
            #Filtrar ações por recursos
            self.choose_combo()
        self.end_of_turn()
    
    def end_of_turn(self):
        for condition in self.conditions:
            condition.notify_EoT(isCaster = False)
        for condition in self.applied_conditions['Concentration']:
            condition.notify_EoT(isCaster = True)
        for condition in self.applied_conditions['Non-Concentration']:
            condition.notify_EoT(isCaster = True)
    
    def check_hit(self, attack_roll):
        if attack_roll >= self.AC:
            print('Ataque de', attack_roll, 'acerta AC de', self.AC)
            return True
        else:
            print('Ataque de', attack_roll, 'erra AC de', self.AC)
            return False
    
    def make_save(self,save_DC,save_type):
        save = d20roll(self.saving_throws[save_type],int(self.save_advantage[save_type]) - int(self.save_disadvantage[save_type]))
        if save >= save_DC:
            print('Saving throw de',self.name,'de',save,'passa contra save DC de',save_DC)
            return True
        else:
            print('Saving throw de',self.name,'de',save,'falha contra save DC de',save_DC)
            return False

    
    def take_damage(self, damage, damage_type):
        if self.damage_type_multipliers.get(damage_type):
            print('dano modificado de', damage, 'para', floor(damage*self.damage_type_multipliers.get(damage_type)), 'devido a resistencias/fraquezas/imunidades')
            damage = floor(damage*self.damage_type_multipliers.get(damage_type))
        self.HP -= damage
        print(self.name, 'toma', damage, 'de dano! HP reduzido para', self.HP)
        if not self.is_alive():
            print(self.name, 'morreu')
            self.simulator.notify_death(self,self.team)
        
    def recover_hit_points(self,amount):
        self.HP += amount
        #Atualmente removendo o cap de max HP até definir lógica de ações
        #if self.HP > self.MHP:
        #    self.HP = self.MHP
        print(self.name, 'recupera',amount,'de hp. Está agora com',self.HP)
    
    def roll_iniciative(self):
        iniciative = d20roll(self.iniciative,0)
        print(self.name, 'rolou', iniciative, 'de iniciativa')
        return iniciative
        
    def is_alive(self):
        if self.HP > 0:
            return True
        else: 
            return False