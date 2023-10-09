from random import choice
from diceroller import d20roll, diceroll
from math import floor

class Creature:

    def __init__(self, name, max_hit_points, armor_class, saving_throws, iniciative):
        self.name = name
        self.MHP = max_hit_points
        self.HP = self.MHP
        self.AC = armor_class
        self.saving_throws = {
            'STR': saving_throws[0],
            'DEX': saving_throws[1],
            'CON': saving_throws[2],
            'INT': saving_throws[3],
            'WIS': saving_throws[4],
            'CHA': saving_throws[5]
        }
        self.iniciative = iniciative
        self.actions = []
        self.bonus_actions = []
        self.damage_type_multipliers = {}
        self.max_resources = {}
        self.current_resources = {}
        self.rest_resources = {}
        self.recharge_resources = {}
        simulator = None
        team = 0
        
    def add_action(self, action):
        self.actions.append(action)
        
    def add_bonus_action(self, action):
        self.bonus_actions.append(action)
        
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
    
    def take_turn(self):
        #No futuro, adicionar aqui lógica de ações
        print('\nTurno de:', self.name)
        #Recharge
        for resource_type, recharge in self.recharge_resources.items():
            if recharge <= diceroll(1,6,0):
                self.current_resources[resource_type] = self.max_resources[resource_type]
                print(self.name,'Recarrega seu',resource_type)
        
        #Filtrar ações por recursos
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
            
        #Filtrar ações bonus por recursos
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
        
    def check_hit(self, attack_roll):
        if attack_roll >= self.AC:
            print('Ataque de', attack_roll, 'acerta AC de', self.AC)
            return True
        else:
            print('Ataque de', attack_roll, 'erra AC de', self.AC)
            return False
    
    def make_save(self,save_DC,save_type):
        save = d20roll(self.saving_throws[save_type],0)
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