from random import sample
from diceroller import d20roll, diceroll
from math import floor

class Action:
    def __init__(self, name, target_number, target_type, attempt, resource_cost = None):
        self.name = name
        self.target_number = target_number
        self.target_type = target_type
        self.attempt = attempt
        self.resource_cost = resource_cost
    
    def act(self, targets, creature):
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
            attack_roll = d20roll(self.attack_bonus,int(self.advantage + target.AC_advantage >0) - int(self.disadvantage + target.AC_disadvantage>0))
            if attack_roll == 20 + self.attack_bonus:
                print('Critico!')
                result_list.append(2)
            else:
                hit = target.check_hit(attack_roll)
                if hit == True:
                    result_list.append(1)
                else:
                    result_list.append(-1)
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

    def act(self,targets,creature):
        result_list = []
        for target in targets:
            passed = target.make_save(self.save_DC,self.save_type)
            if passed == False:
                result_list.append(1)
            elif self.half_on_save:
                result_list.append(0)
            else:
                result_list.append(-1)
        self.effect.apply(targets,result_list,creature)

class Effect:
    def __init__(self):
        pass
    
    def apply(self, target):
        pass

class Damage(Effect):
    
    def __init__(self, damage_die_amount, damage_die_size, damage_modifier, damage_type, follow_attack = None, follow_attempt = None, follow_effect = None):
        self.damage_die_amount = damage_die_amount
        self.damage_die_size = damage_die_size
        self.damage_modifier = damage_modifier
        self.damage_type = damage_type
        self.follow_attack = follow_attack
        self.follow_attempt = follow_attempt
        self.follow_effect = follow_effect
    
    def apply(self, targets, result_list, creature):
        if len(targets) > 1:
            damage = diceroll(self.damage_die_amount,self.damage_die_size,self.damage_modifier)
            half_damage = floor(damage/2)
            for i in range(len(targets)):
                if result_list[i] == 1:
                    targets[i].take_damage(damage,self.damage_type)
                elif result_list[i] == 0:
                    targets[i].take_damage(half_damage,self.damage_type)
        elif len(targets) == 1:
            if result_list[0] == 1:
                damage = diceroll(self.damage_die_amount,self.damage_die_size,self.damage_modifier)
                targets[0].take_damage(damage,self.damage_type)
            elif result_list[0] == 2:
                crit_damage = diceroll(2*self.damage_die_amount,self.damage_die_size,self.damage_modifier)
                targets[0].take_damage(crit_damage,self.damage_type)
        if self.follow_attack:
            self.follow_attack.act(targets)
        if self.follow_attempt:
            self.follow_attempt.act(targets)
        if self.follow_effect:
            self.follow_effect.apply(targets,result_list,creature)

class Healing(Effect):
    
    def __init__(self, healing_die_amount, healing_die_size, healing_modifier):
        self.healing_die_amount = healing_die_amount
        self.healing_die_size = healing_die_size
        self.healing_modifier = healing_modifier
    
    def apply(self, targets, result_list, creature):
        amount = diceroll(self.healing_die_amount,self.healing_die_size,self.healing_modifier)
        for target in targets:
            target.recover_hit_points(amount)

class Apply_Condition(Effect):

    def __init__(self, condition, concentration = False):
        self.condition = condition
        self.concentration = concentration
        
    def apply(self, targets, result_list, creature):
        for i in range(len(targets)):
            if result_list[i] >=1:
                creature.add_applied_condition(self.condition, self.concentration)
                targets[i].add_condition(self.condition)
                self.condition.add_caster_target(creature, targets[i])

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
#            print('Critico!')
#            hit = True
#            damage = diceroll(2*self.damage_die_amount,self.damage_die_size,self.damage_modifier)
#            target.take_damage(damage, self.damage_type)
#        else:
#            hit = target.check_hit(attack_roll)
#            if hit == True:
#                damage = diceroll(self.damage_die_amount,self.damage_die_size,self.damage_modifier)
#                target.take_damage(damage, self.damage_type)
#            