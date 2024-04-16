from random import sample
from diceroller import d20roll, diceroll
from math import floor
import logger
import logging
import copy

class Action:
    def __init__(self, name, target_number, target_type, attempt, resource_cost = None, tags = [], is_concentration = False):
        self.name = name
        self.target_number = target_number
        self.target_type = target_type
        self.attempt = attempt
        self.resource_cost = resource_cost
        self.tags = tags
        self.is_concentration = is_concentration
    
    def act(self, targets, creature):
        if self.is_concentration: creature.lose_concentration()
        logging.info(f'{creature.name} usa {self.name} contra {[target.name for target in targets]}')
        if self.resource_cost:
            creature.current_resources[self.resource_cost[0]] -= self.resource_cost[1]
        self.attempt.act(targets, creature)
    
    def get_targets(self, creature):
        if self.target_type == 'Self':
            return [creature]
        elif self.target_type == 'Enemy':
            enemies = creature.simulator.get_enemy_team(creature.team)
            if self.target_number >= len(enemies):
                return enemies
            else:
                return sample(enemies,self.target_number)
        elif self.target_type == 'Ally':
            allies = creature.simulator.get_allied_team(creature.team)
            if self.target_number >= len(allies):
                return allies
            else:
                return sample(allies,self.target_number)

class Attempt:
    def __init__(self):
        pass
    
    def act(self, target, creature):
        pass

class Attack_Roll(Attempt):

    def __init__(self,attack_bonus,effect):
        self.attack_bonus = attack_bonus
        self.effect = effect
        self.advantage = 0
        self.disadvantage = 0

    def act(self,targets,creature):
        result_list = []
        for target in targets:
            paired_conditions = []
            for condition in target.conditions:
                if condition.is_paired == True and condition.caster == creature:
                    paired_conditions.append(condition)
            for paired_condition in paired_conditions:
                paired_condition.apply_condition()
            attack_roll = d20roll(self.attack_bonus,int(self.advantage + target.AC_advantage >0) - int(self.disadvantage + target.AC_disadvantage>0))
            hit = target.check_hit(attack_roll)
            if (attack_roll >= creature.crits_on + self.attack_bonus) or (target.auto_crit == True and hit == True):
                logging.info('Critico!')
                result_list.append(2)
            else:
                if hit == True:
                    result_list.append(1)
                else:
                    result_list.append(-1)
            for paired_condition in paired_conditions:
                paired_condition.unapply_condition()
        self.effect.apply(targets,result_list,creature)

class Auto_Apply(Attempt):

    def __init__(self,effect):
        self.effect = effect
    
    def act(self,targets,creature):
        result_list = [1 for i in range(len(targets))]
        self.effect.apply(targets,result_list,creature)

class Saving_Throw(Attempt):

    def __init__(self,save_DC,save_type,half_on_save,effect):
        self.save_DC = save_DC
        self.save_type = save_type
        self.half_on_save = half_on_save
        self.effect = effect
        if isinstance(self.effect, Apply_Condition):
            self.effect.condition.saving_throw = [save_DC,save_type]

    def act(self,targets,creature):
        result_list = []
        for target in targets:
            paired_conditions = []
            for condition in target.conditions:
                if condition.is_paired == True and condition.caster == creature:
                    paired_conditions.append(condition)
            for paired_condition in paired_conditions:
                paired_condition.apply_condition()
            target_has_evasion = target.evasion[self.save_type]
            passed = target.make_save(self.save_DC,self.save_type)
            if passed == False:
                if (target_has_evasion == True and self.half_on_save):
                    result_list.append(0)
                else: result_list.append(1)
            elif passed == True:
                if (target_has_evasion == True and self.half_on_save):
                    result_list.append(-1)
                else: result_list.append(0)
            else:
                result_list.append(-1)
            for paired_condition in paired_conditions:
                paired_condition.unapply_condition()
        self.effect.apply(targets,result_list,creature, saving_throw = True)

class Effect:
    def __init__(self):
        pass
    
    def apply(self, target):
        pass

class Damage(Effect):
    
    def __init__(self, damage, follow_actions = []):
        self.damage = damage #damage tem a forma [quantidade de dados, tamanho de dados, modifier, tipo de dano]
        self.follow_actions = follow_actions
    
    def add_damage_modifier(self, damage_modifier):
        self.damage[0][2] += damage_modifier #Modifiers a mais afetam somente o primeiro dano
        
    def add_extra_damage(self, damage):
        self.damage.append(damage)
    
    def remove_damage(self, damage):
        self.damage.remove(damage)
    
    def apply(self, targets, result_list, creature, saving_throw = False):
        if saving_throw:
            total_damage = []
            total_half_damage = []
            for damage_parcel in self.damage:
                damage = diceroll(damage_parcel[0],damage_parcel[1],damage_parcel[2])
                half_damage = floor(damage/2)
                total_damage.append([damage,damage_parcel[3]])
                total_half_damage.append([half_damage,damage_parcel[3]])
            for i in reversed(range(len(targets))):
                paired_conditions = []
                for condition in targets[i].conditions:
                    if condition.is_paired == True and condition.caster == creature:
                        paired_conditions.append(condition)
                for paired_condition in paired_conditions:
                    paired_condition.apply_condition()
                if result_list[i] == 1:
                    alive = targets[i].take_damage(total_damage)
                    for follow_action in self.follow_actions:
                        possible = True
                        if not alive: possible = False
                        if follow_action.resource_cost:
                            if creature.current_resources[follow_action.resource_cost[0]] < follow_action.resource_cost[1]: possible = False
                        if possible: 
                            follow_value = creature.intelligence.choose_action([[follow_action]], [creature], [targets[i]], creature)
                            if follow_value[0][0][0] > 0: follow_action.act([targets[i]], creature)
                elif result_list[i] == 0:
                    targets[i].take_damage(total_half_damage)
                for paired_condition in paired_conditions:
                    paired_condition.unapply_condition()
        else:
            if result_list[0] == 1:
                paired_conditions = []
                for condition in targets[0].conditions:
                    if condition.is_paired == True and condition.caster == creature:
                        paired_conditions.append(condition)
                for paired_condition in paired_conditions:
                    paired_condition.apply_condition()
                total_damage = []
                for damage_parcel in self.damage:
                    damage = diceroll(damage_parcel[0],damage_parcel[1],damage_parcel[2])
                    total_damage.append([damage,damage_parcel[3]])
                alive = targets[0].take_damage(total_damage)
                for follow_action in self.follow_actions:
                    possible = True
                    if not alive: possible = False
                    if follow_action.resource_cost:
                        if creature.current_resources[follow_action.resource_cost[0]] < follow_action.resource_cost[1]: possible = False
                    if possible: 
                        follow_value = creature.intelligence.choose_action([[follow_action]], [creature], [targets[0]], creature)
                        if follow_value[0][0][0] > 0: follow_action.act([targets[0]], creature)
                for paired_condition in paired_conditions:
                    paired_condition.unapply_condition()
            elif result_list[0] == 2:
                paired_conditions = []
                for condition in targets[0].conditions:
                    if condition.is_paired == True and condition.caster == creature:
                        paired_conditions.append(condition)
                for paired_condition in paired_conditions:
                    paired_condition.apply_condition()
                total_crit_damage = []
                for damage_parcel in self.damage:
                    crit_damage = diceroll(damage_parcel[0]*2,damage_parcel[1],damage_parcel[2])
                    total_crit_damage.append([crit_damage,damage_parcel[3]])
                alive = targets[0].take_damage(total_crit_damage)
                for follow_action in self.follow_actions:
                    possible = True
                    if not alive: possible = False
                    if follow_action.resource_cost:
                        if creature.current_resources[follow_action.resource_cost[0]] < follow_action.resource_cost[1]: possible = False
                    if possible: 
                        follow_value = creature.intelligence.choose_action([[follow_action]], [creature], [targets[0]], creature)
                        if follow_value[0][0][0] > 0: follow_action.act([targets[0]], creature)
                for paired_condition in paired_conditions:
                    paired_condition.unapply_condition()

class Healing(Effect):
    
    def __init__(self, healing_die_amount, healing_die_size, healing_modifier):
        self.healing_die_amount = healing_die_amount
        self.healing_die_size = healing_die_size
        self.healing_modifier = healing_modifier
    
    def apply(self, targets, result_list, creature, saving_throw = False):
        amount = diceroll(self.healing_die_amount,self.healing_die_size,self.healing_modifier)
        for target in targets:
            target.recover_hit_points(amount)

class Apply_Condition(Effect):

    def __init__(self, condition, concentration = False):
        self.condition = condition
        self.concentration = concentration
        
    def apply(self, targets, result_list, creature, saving_throw = True):
        for i in range(len(targets)):
            if result_list[i] >=1:
                new_condition = copy.deepcopy(self.condition)
                creature.add_applied_condition(new_condition, self.concentration)
                targets[i].add_condition(new_condition)
                new_condition.add_caster_target(creature, targets[i])

#class Basic_Attack(Action):
#    
#    def __init__(self,name,attack_bonus,damage_die_amount,damage_die_size,damage_modifier,damage_type):
#        self.name = name
#        self.attack_bonus = attack_bonus
#        self.damage_die_amount = damage_die_amount
#        self.damage_die_size = damage_die_size
#        self.damage_modifier = damage_modifier
#        self.damage_type = damage_type
#        self.advantage = 0
#
#    def act(self,target):
#        #roll attack
#        attack_roll = d20roll(self.attack_bonus,self.advantage)
#        if attack_roll == 20 + self.attack_bonus:
#            logging.info('Critico!')
#            hit = True
#            damage = diceroll(2*self.damage_die_amount,self.damage_die_size,self.damage_modifier)
#            target.take_damage(damage, self.damage_type)
#        else:
#            hit = target.check_hit(attack_roll)
#            if hit == True:
#                damage = diceroll(self.damage_die_amount,self.damage_die_size,self.damage_modifier)
#                target.take_damage(damage, self.damage_type)
#            