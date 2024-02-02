import action as act
from diceroller import diceroll

#End condition types:
# Start of Caster Turn
# End of Caster Turn
# Start of Target Turn
# End of Target Turn
# On Damage Taken
# Repeat Save on End of Target Turn
# Repeat Save on Damage Taken

class Condition:

    def __init__(self, name, end_condition, max_duration, condition_effects, saving_throw = None):
        self.name = name
        self.end_condition = end_condition
        self.max_duration = max_duration
        self.duration = max_duration
        #self.effect_type = effect_type
        self.condition_effects = condition_effects
        self.saving_throw = saving_throw
        self.caster = None
        self.target = None
        
    def add_caster_target(self, caster, target):
        self.caster = caster
        self.target = target
        self.duration = self.max_duration
        for effect in self.condition_effects:
            effect.apply_effect(target)
        
    def notify_SoT(self, isCaster = True):
        if self.end_condition == "Start of Caster Turn" and isCaster:
            self.duration -= 1
        elif self.end_condition == "Start of Target Turn" and not isCaster:
            for effect in self.condition_effects:
                effect.notify_SoT(self.target)
            self.duration -= 1
        if self.duration <= 0:
            self.remove_condition()
            
    def notify_EoT(self, isCaster = True):
        if self.end_condition == "End of Caster Turn" and isCaster:
            self.duration -= 1
        elif self.end_condition == "End of Target Turn" and not isCaster:
            for effect in self.condition_effects:
                effect.notify_EoT(self.target)
            self.duration -= 1
        elif self.end_condition == "Repeat Save on End of Target Turn" and not isCaster:
            for effect in self.condition_effects:
                effect.notify_EoT(self.target)
            self.duration -= 1
            if self.target.make_save(self.saving_throw[0], self.saving_throw[1]): self.remove_condition
        if self.duration <= 0:
            self.remove_condition()
    
    def notify_damaged(self):
        if self.end_condition == "On Damage Taken":
            self.remove_condition()
        elif self.end_condition == "Repeat Save on Damage Taken":
            if self.target.make_save(self.saving_throw[0], self.saving_throw[1]): self.remove_condition
    
    def remove_condition(self):
        print(f'Removing condition {self.name}')
        for effect in self.condition_effects:
            effect.remove_effect(self.target)
        self.caster.remove_applied_condition(self)
        self.target.remove_condition(self)
    
class Condition_Effect:

    def __init__(self):
        pass
        
    def apply_effect(self, target):
        pass
        
    def remove_effect(self,target):
        pass
        
    def notify_SoT(self,target):
        pass
        
    def notify_EoT(self,target):
        pass
        
class Modified_Attack(Condition_Effect):

    def __init__(self, attack_bonus = 0, damage_bonus = 0, advantage = 0, extra_damage = [], crit_threshold = 20):
        self.attack_bonus = attack_bonus
        self.damage_bonus = damage_bonus
        self.advantage = advantage
        self.extra_damage = extra_damage
        self.crit_threshold = crit_threshold
        
    def apply_effect(self, target):
        if self.crit_threshold != 20: target.crits_on = self.crit_threshold
        for action in target.actions:
            if isinstance(action.attempt, act.Attack_Roll):
                action.attempt.attack_bonus += self.attack_bonus
                if self.advantage == 1:
                    action.attempt.advantage += 1
                elif self.advantage == -1:
                    action.attempt.disadvantage += 1
                if isinstance(action.attempt.effect, act.Damage):
                    action.attempt.effect.add_damage_modifier(self.damage_bonus)
                    if self.extra_damage:
                        action.attempt.effect.add_extra_damage(self.extra_damage)
                    
    def remove_effect(self,target):
        if self.crit_threshold != 20: target.crits_on = 20
        for action in target.actions:
            if isinstance(action.attempt, act.Attack_Roll):
                action.attempt.attack_bonus -= self.attack_bonus
                if self.advantage == 1:
                    action.attempt.advantage -= 1
                elif self.advantage == -1:
                    action.attempt.disadvantage -= 1
                if isinstance(action.attempt.effect, act.Damage):
                    action.attempt.effect.add_damage_modifier(-self.damage_bonus)
                    if self.extra_damage:
                        action.attempt.effect.remove_damage(extra_damage)

class Modified_Defense(Condition_Effect):

    def __init__(self, AC_bonus = 0, ac_advantage = 0, save_bonus = [0,0,0,0,0,0], save_advantage = [0,0,0,0,0,0], damage_type_multipliers = {}, damage_type_reductions = {}, auto_crit = False):
        self.AC_bonus = AC_bonus
        self.save_bonus = save_bonus
        self.ac_advantage = ac_advantage
        self.save_advantage = save_advantage
        self.damage_type_multipliers = damage_type_multipliers
        self.damage_type_reductions = damage_type_reductions
        self.auto_crit = auto_crit
    
    def apply_effect(self, target):
        target.AC += self.AC_bonus
        target.auto_crit = self.auto_crit
        if self.ac_advantage == 1:
            target.AC_advantage += 1
        elif self.ac_advantage == -1:
            target.AC_disadvantage += 1
        for i in range(6):
            target.saving_throws[i] += self.save_bonus[i]
            if target.save_advantage[i] == 1:
                target.save_advantage[i] += 1
            elif target.save_advantage[i] == -1:
                target.save_disadvantage[i] += 1
        for damage_type, damage_multiplier in self.damage_type_multipliers.items():
            target.damage_type_multipliers[damage_type] = damage_multiplier
        for damage_type, damage_reduction in self.damage_type_reductions.items():
            target.damage_type_reductions[damage_type] = damage_reduction
            
    def remove_effect(self, target):
        target.AC -= self.AC_bonus
        target.auto_crit = False
        if self.ac_advantage == 1:
            target.AC_advantage -= 1
        elif self.ac_advantage == -1:
            target.AC_disadvantage -= 1
        for i in range(6):
            target.saving_throws[i] -= self.save_bonus[i]
            if target.save_advantage[i] == 1:
                target.save_advantage[i] -= 1
            elif target.save_advantage[i] == -1:
                target.save_disadvantage[i] -= 1
        for damage_type, damage_multiplier in self.damage_type_multipliers.items():
            del target.damage_type_multipliers[damage_type]
        for damage_type, damage_reduction in self.damage_type_reductions.items():
            del target.damage_type_reductions[damage_type]
        
            
class Modified_Economy(Condition_Effect):

    def __init__(self, action_modifier = 0, bonus_action_modifier = 0, reaction_modifier = 0):
        self.action_modifier = action_modifier
        self.bonus_action_modifier = bonus_action_modifier
        self.reaction_modifier = reaction_modifier
        
    def apply_effect(self, target):
        target.action_number += self.action_modifier
        target.bonus_action_number += self.bonus_action_modifier
        target.reaction_number += self.reaction_modifier
        
    def remove_effect(self,target):
        target.action_number -= self.action_modifier
        target.bonus_action_number -= self.bonus_action_modifier
        target.reaction_number -= self.reaction_modifier
        
class Effect_Over_Time(Condition_Effect):
    def __init__(self, damage = [], healing = []):
        self.damage = damage
        self.healing = healing
        
    def notify_SoT(self,target):
        if self.damage:
            target.take_damage(diceroll(self.damage[0],self.damage[1],self.damage[2]),self.damage_3)
        if self.healing:
            target.recover_hit_points(diceroll(self.healing[0],self.healing[1],self.healing[2]))
        
    def notify_EoT(self,target):
        if self.damage:
            target.take_damage(diceroll(self.damage[0],self.damage[1],self.damage[2]),self.damage_3)
        if self.healing:
            target.recover_hit_points(diceroll(self.healing[0],self.healing[1],self.healing[2]))
    