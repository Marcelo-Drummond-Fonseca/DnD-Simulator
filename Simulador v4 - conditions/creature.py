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
            "Concentration": []
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
    
    def remove_condition(self, condition):
        self.conditions.remove(condition)
    
    def start_of_turn(self):
        for condition in self.conditions:
            condition.notify_SoT(self)
        for condition in self.applied_conditions:
            condition.notify_SoT(self)
        self.take_turn()
    
    def take_turn(self):
        #No futuro, adicionar aqui lógica de ações
        print('\nTurno de:', self.name)
        #Recharge
        for resource_type, recharge in self.recharge_resources.items():
            if recharge <= diceroll(1,6,0):
                self.current_resources[resource_type] = self.max_resources[resource_type]
                print(self.name,'Recarrega seu',resource_type)
        
        #Filtrar Free actions por recursos
        
        possible_free_actions = []
        for free_actions in self.free_actions:
            possible = True
            necessary_resources = {}
            for free_action in free_actions:
                if free_action.resource_cost:
                    if free_action.resource_cost[0] in necessary_resources:
                        necessary_resources[free_action.resource_cost[0]] += free_action.resource_cost[1]
                    else:
                        necessary_resources[free_action.resource_cost[0]] = free_action.resource_cost[1]
            for resource_type, resource_amount in necessary_resources.items():
                if self.current_resources[resource_type] < resource_amount:
                    possible = False
            if possible:
                possible_free_actions.append(free_actions)
        if possible_free_actions:
            free_actions = choice(possible_free_actions)
            for free_action in free_actions:
                targets = free_action.get_targets(self)
                print(self.name, 'usa', free_action.name, 'contra', *(getattr(creature, "name") for creature in targets))
                if free_action.resource_cost:
                    self.current_resources[free_action.resource_cost[0]] -= free_action.resource_cost[1]
                free_action.act(targets)
        
        #Filtrar ações bonus por recursos
        for i in range(bonus_action_number):
            possible_bonus_actions = []
            for bonus_actions in self.bonus_actions:
                possible = True
                necessary_resources = {}
                for bonus_action in bonus_actions:
                    if bonus_action.resource_cost:
                        if bonus_action.resource_cost[0] in necessary_resources:
                            necessary_resources[bonus_action.resource_cost[0]] += bonus_action.resource_cost[1]
                        else:
                            necessary_resources[bonus_action.resource_cost[0]] = bonus_action.resource_cost[1]
                for resource_type, resource_amount in necessary_resources.items():
                    if self.current_resources[resource_type] < resource_amount:
                        possible = False
                if possible:
                    possible_bonus_actions.append(bonus_actions)
            if possible_bonus_actions:
                bonus_actions = choice(possible_bonus_actions)
                for bonus_action in bonus_actions:
                    targets = bonus_action.get_targets(self)
                    print(self.name, 'usa', bonus_action.name, 'contra', *(getattr(creature, "name") for creature in targets))
                    if bonus_action.resource_cost:
                        self.current_resources[bonus_action.resource_cost[0]] -= bonus_action.resource_cost[1]
                    bonus_action.act(targets)
        
        #Filtrar ações por recursos
        for i in range(action_number):
            possible_actions = []
            for actions in self.actions:
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
                action.act(targets)
            
        self.end_of_turn()
    
    def end_of_turn():
        for condition in self.conditions:
            condition.notify_EoT(self)
        for condition in self.applied_conditions:
            condition.notify_EoT(self)
    
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
        if self.HP > self.MHP:
            self.HP = self.MHP
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