from random import choice
from diceroller import d20roll, diceroll
from math import floor
from intelligence import Intelligence
import random

ai_modifiers = {
    'Damage': {
        'damage_favor': 1.5, 
        'healing_favor': 0.75, 
        'self_buff_favor': 1.25, 
        'ally_buff_favor': 0.75, 
        'debuff_favor': 0.9
    },
    'Tank': {
        'damage_favor': 1.25, 
        'healing_favor': 1, 
        'self_buff_favor': 1.5, 
        'ally_buff_favor': 0.75, 
        'debuff_favor': 1
    },
    'Support': {
        'damage_favor': 0.75, 
        'healing_favor': 1.5, 
        'self_buff_favor': 0.85, 
        'ally_buff_favor': 1.5, 
        'debuff_favor': 1.5
    },
    'Neutral': {
        'damage_favor': 1, 
        'healing_favor': 1, 
        'self_buff_favor': 1, 
        'ally_buff_favor': 1, 
        'debuff_favor': 1
    }
}
ai_target_modifiers = {
    'Damage': {
        'Tank': 1.2, 
        'Damage': 1, 
        'Support': 0.9, 
        'Neutral': 1
    },
    'Tank': {
        'Tank': 2, 
        'Damage': 1, 
        'Support': 0.75, 
        'Neutral': 1
    },
    'Support': {
        'Tank': 1.5, 
        'Damage': 1, 
        'Support': 1,
        'Neutral': 1
    },
    'Neutral': {
        'Tank': 1, 
        'Damage': 1, 
        'Support': 1, 
        'Neutral': 1
    }
}

class Creature:

    def __init__(self, name, max_hit_points, armor_class, saving_throws, iniciative, AI_type = 'Neutral', tags = []):
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
        self.follow_actions = []
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
        self.permanent_conditions = []
        self.conditions = []
        self.applied_conditions = {
            "Concentration": [],
            "Non-Concentration": []
        }
        self.simulator = None
        self.team = 0
        self.AI_type = AI_type
        self.tags = tags
        self.intelligence = Intelligence(True,ai_modifiers[self.AI_type],ai_target_modifiers[self.AI_type])
        self.crits_on = 20 #Quanto precisa rolar pra um ataque ser crítico
        self.auto_crit = False #Qualquer ataque que acerta essa criatura é um crítico
        
    def add_action(self, action):
        self.actions.append(action)
        
    def add_bonus_action(self, action):
        self.bonus_actions.append(action)
    
    def add_free_action(self, action):
        self.free_actions.append(action)
    
    def add_follow_action(self, action):
        self.follow_action.append(action)
    
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
        
    def add_resource(self, resource_type, resource_amount, regain_type):
        self.max_resources[resource_type] = resource_amount
        self.current_resources[resource_type] = resource_amount
        if regain_type == 'Short Rest':
            self.rest_resources[resource_type] = 'Short Rest'
        elif regain_type == 'Long Rest':
            self.rest_resources[resource_type] = 'Long Rest'
        elif regain_type.startswith('Recharge'):
            self.recharge_resources[resource_type] = int(regain_type.split()[1])
    
    def remove_all_conditions(self):
        for condition in self.conditions:
            condition.remove_condition()
        for condition in self.applied_conditions['Concentration']:
            condition.remove_condition()
        for condition in self.applied_conditions['Non-Concentration']:
            condition.remove_condition()
        
    
    def full_restore(self):
        self.HP = self.MHP
        for resource_type, resource_amount in self.max_resources.items():
            self.current_resources[resource_type] = self.max_resources[resource_type]
        self.remove_all_conditions()
    
    def add_simulator(self, simulator, team):
        self.simulator = simulator
        self.team = team
        
    def add_permanent_condition(self, condition):
        self.permanent_conditions.append(condition)
        print(condition.name)
    
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
    
    def lose_concentration(self):
        for condition in self.applied_conditions['Concentration']:
            print(f'{self.name} perde concentration em {condition.name}')
            condition.remove_condition()
    
    def choose_combo(self, options, by_index):
        possible_actions = []
        for combo in options:
            if by_index:
                actions = [self.actions[i] for i in combo]
            else:
                actions = combo
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
        if possible_actions:
            allied_team = self.simulator.get_allied_team(self.team)
            enemy_team = self.simulator.get_enemy_team(self.team)
            original_enemy_team = enemy_team.copy()
            all_scores = self.intelligence.choose_action(possible_actions,allied_team,enemy_team,self)
            all_scores_best = []
            for i, combo_scores in enumerate(all_scores):
                score_sum = 0
                for j, action_scores in enumerate(combo_scores):
                    target_number = possible_actions[i][j].target_number
                    best_score = sum(sorted(action_scores, reverse=True)[:target_number])
                    score_sum += best_score
                all_scores_best.append(score_sum)
            average_score = sum(all_scores_best)/len(all_scores_best)
            filtered_scores_averages = [value for value in all_scores_best if value >= average_score and value > 0]
            filtered_scores = [all_scores[i] for i, value in enumerate(all_scores_best) if value >= average_score and value > 0]
            filtered_combos = [possible_actions[i] for i, value in enumerate(all_scores_best) if value >= average_score and value > 0]
            if filtered_combos:
                selected_index = random.choices(range(len(filtered_combos)), weights=filtered_scores_averages, k=1)[0]
                selected_combo = filtered_combos[selected_index]
                selected_scores = filtered_scores[selected_index]
                for i, action in enumerate(selected_combo):
                    if action.target_type == 'Self':
                        action.act([self],self)
                    elif action.target_type == 'Enemy':      
                        if len(enemy_team) != len(selected_scores[i]):
                            original_team = set(original_enemy_team)
                            new_team = set(enemy_team)
                            missing_members = original_team - new_team
                            missing_index = [i for i, enemy in enumerate(original_enemy_team) if enemy in missing_members]
                            considered_scores = [score for i, score in enumerate(selected_scores[i]) if i not in missing_index]
                            if not considered_scores: break
                        else: considered_scores = selected_scores[i]
                        
                        if action.target_number >= len(enemy_team):
                            action.act(enemy_team,self)
                        else:
                            zipped_enemy_scores = list(zip(enemy_team, considered_scores))
                            sorted_enemy_scores = sorted(zipped_enemy_scores, key=lambda x: x[1], reverse=True)
                            targets = [enemy[0] for enemy in sorted_enemy_scores[:action.target_number]]
                            action.act(targets,self)
                    elif action.target_type == 'Ally':
                        if action.target_number >= len(allied_team):
                            action.act(allied_team,self)
                        else:
                            zipped_ally_scores = list(zip(allied_team, selected_scores[i]))
                            sorted_ally_scores = sorted(zipped_ally_scores, key=lambda x: x[1], reverse=True)
                            targets = [ally[0] for ally in sorted_ally_scores[:action.target_number]]
                            action.act(targets,self)
                    
                
            
        
        
        #for action in actions:
            #target = choice(self.simulator.get_enemy_team(self.team))
        #    targets = action.get_targets(self)
        #    print(self.name, 'usa', action.name, 'contra', *(getattr(creature, "name") for creature in targets))
        #    if action.resource_cost:
        #        self.current_resources[action.resource_cost[0]] -= action.resource_cost[1]
        #    action.act(targets, self)
        
    
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
        for condition in self.permanent_conditions:
            condition.notify_SoT(isCaster = False)
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
        self.choose_combo([[free_action] for free_action in self.free_actions], False)
        for i in range(self.bonus_action_number):
            #Filtrar ações bonus por recursos
            self.choose_combo([[bonus_action] for bonus_action in self.bonus_actions], False)
        for i in range(self.action_number):
            #Filtrar ações por recursos
            self.choose_combo(self.combos, True)
        self.end_of_turn()
    
    def end_of_turn(self):
        for condition in self.permanent_conditions:
            condition.notify_EoT(isCaster = False)
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

    
    def take_damage(self, total_damage):
        total_damage_taken = 0
        for damage_tuple in total_damage:
            damage = damage_tuple[0]
            damage_type = damage_tuple[1]
            if self.damage_type_multipliers.get(damage_type):
                print('dano modificado de', damage, 'para', floor(damage*self.damage_type_multipliers.get(damage_type)), 'devido a resistencias/fraquezas/imunidades')
                damage = floor(damage*self.damage_type_multipliers.get(damage_type))
            self.HP -= damage
            print(f'{self.name} toma {damage} de dano. está agora com {self.HP} de vida')
            total_damage_taken += damage
            if not self.is_alive():
                print(self.name, 'morreu')
                self.simulator.notify_death(self,self.team)
                self.remove_all_conditions()
                self.lose_concentration()
                return False
        if total_damage_taken > 0 and self.applied_conditions["Concentration"]:
            if not self.make_save(max(10,total_damage_taken/2),2):
                self.lose_concentration()
        for condition in self.conditions:
            condition.notify_damaged()
        return True
        
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