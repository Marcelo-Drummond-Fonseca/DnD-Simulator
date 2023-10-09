from random import choice
from diceroller import d20roll, diceroll
from math import floor

class Creature:
    simulator = None
    team = 0
    damage_type_multipliers = {}

    def __init__(self, name, max_hit_points, armor_class, iniciative):
        self.name = name
        self.MHP = max_hit_points
        self.HP = self.MHP
        self.AC = armor_class
        #self.saving_throws = saving_throws
        self.iniciative = iniciative
        self.actions = []
        
    def add_action(self, action):
        self.actions.append(action)
        
    def add_damage_type_multiplier(self, damage_type, multiplier):
        self.damage_type_multipliers[damage_type] = multiplier
    
    def add_simulator(self, simulator, team):
        self.simulator = simulator
        self.team = team
    
    def take_turn(self):
        #No futuro, adicionar aqui lógica de ações
        print('\nTurno de:', self.name)
        action = choice(self.actions)
        target = choice(self.simulator.get_enemy_team(self.team))
        print(self.name, 'usa', action.name, 'contra', target.name)
        action.act(target)
        
    def check_hit(self, attack_roll):
        if attack_roll >= self.AC:
            print('Ataque de', attack_roll, 'acerta AC de', self.AC)
            return True
        else:
            print('Ataque de', attack_roll, 'erra AC de', self.AC)
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
        
    def roll_iniciative(self):
        iniciative = d20roll(self.iniciative,0)
        print(self.name, 'rolou', iniciative, 'de iniciativa')
        return iniciative
        
    def is_alive(self):
        if self.HP > 0:
            return True
        else: 
            return False