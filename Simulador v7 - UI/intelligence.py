import action as act
from math import floor
import logger
import logging

class Intelligence:

    def __init__(self, public_knowledge, modifiers = {'damage_favor': 1, 'healing_favor': 1, 'self_buff_favor': 1, 'ally_buff_favor': 1, 'debuff_favor': 1}, target_modifiers = {'Tank': 1, 'Damage': 1, 'Support': 1, 'Neutral': 1}):
        self.public_knowledge = public_knowledge
        self.modifiers = modifiers
        self.target_modifiers = target_modifiers
        
    

    def choose_action(self, combo_list,allied_team,enemy_team, creature):
        final_scores = []
        for combo in combo_list:
            combo_score = []
            for action in combo:
                final_multiplier = 1
                if action.is_concentration == True:
                    if creature.applied_conditions['Concentration']:
                        final_multiplier *= 0.25
                    else:
                        final_multiplier *= 1.1
                action_score = []
                #Pure Damage
                if isinstance(action.attempt.effect, act.Damage):
                    final_multiplier *= self.modifiers['damage_favor']
                    for enemy in enemy_team:
                        target_multiplier = self.target_modifiers[enemy.AI_type]
                        avg_damage = [d[0]*((d[1]+1)/2)+d[2] for d in action.attempt.effect.damage]
                        #Attack Roll
                        if isinstance(action.attempt, act.Attack_Roll):
                            advantage = int(action.attempt.advantage + enemy.AC_advantage >0) - int(action.attempt.disadvantage + enemy.AC_disadvantage>0)
                            if self.public_knowledge == False:
                                if advantage == 1: avg_damage = [damage*1.5 for damage in avg_damage]
                                elif advantage == -1: avg_damage = [damage*0.5 for damage in avg_damage]
                            else:
                                for i in range(len(avg_damage)):
                                    avg_damage[i] = avg_damage[i]*((max(1,20 - (enemy.AC - action.attempt.attack_bonus) + 1 + (advantage*4)))/20)
                                    if action.attempt.effect.damage[i][3] in enemy.damage_type_multipliers:
                                        avg_damage[i] = avg_damage[i]*enemy.damage_type_multipliers[action.attempt.effect.damage[i][3]]
                        elif isinstance(action.attempt, act.Saving_Throw):
                            avg_half_damage = [floor(damage/2) for damage in avg_damage]
                            save_type = action.attempt.save_type
                            advantage = int(enemy.save_advantage[save_type]) - int(enemy.save_disadvantage[save_type])
                            if self.public_knowledge == False:
                                if advantage == 1: avg_damage = [damage*0.75 for damage in avg_damage]
                                elif advantage == -1: avg_damage = [damage*1.25 for damage in avg_damage]
                            else:
                                for i in range(len(avg_damage)):
                                    hit_chance = (max(0,action.attempt.save_DC - enemy.saving_throws[save_type] - 1 - (advantage*4)))/20
                                    avg_damage[i] = avg_damage[i]*hit_chance + avg_half_damage[i]*(1-hit_chance)
                                    if action.attempt.effect.damage[i][3] in enemy.damage_type_multipliers:
                                        avg_damage[i] = avg_damage[i]*enemy.damage_type_multipliers[action.attempt.effect.damage[i][3]]
                        total_avg_damage = sum(avg_damage)
                        action_score.append(total_avg_damage * final_multiplier * target_multiplier)
                        
                #Pure Healing
                elif isinstance(action.attempt.effect, act.Healing):
                    final_multiplier *= self.modifiers['healing_favor']
                    for ally in allied_team:
                        target_multiplier = self.target_modifiers[ally.AI_type]
                        avg_healing = action.attempt.effect.healing_die_amount*((action.attempt.effect.healing_die_size+1)/2)+action.attempt.effect.healing_modifier
                        if ally.MHP - ally.HP < avg_healing:
                            avg_healing = 0
                        #avg_healing = min(avg_healing, ally.MHP - ally.HP)
                        action_score.append(avg_healing * final_multiplier * target_multiplier)
                        
                #Condition
                elif isinstance(action.attempt.effect, act.Apply_Condition):
                    #Self-Buff
                    if action.target_type == 'Self':
                        final_multiplier *= self.modifiers['self_buff_favor']
                        target_multiplier = self.target_modifiers[creature.AI_type]
                        if action.attempt.effect.condition.name in [condition.name for condition in creature.conditions] and action.attempt.effect.condition.duration>1:
                            if action.resource_cost:
                                action_score.append(-999)
                            else:
                                action_score.append(0)
                        else:
                            action_score.append(creature.HP/2 * final_multiplier * target_multiplier)
                    
                    #Ally Buff
                    elif action.target_type == 'Ally':
                        final_multiplier *= self.modifiers['ally_buff_favor']
                        for ally in allied_team:
                            target_multiplier = self.target_modifiers[ally.AI_type]
                            if action.attempt.effect.condition.name in [condition.name for condition in ally.conditions] and action.attempt.effect.condition.duration>1:
                                if action.resource_cost:
                                    action_score.append(-999)
                                else:
                                    action_score.append(0)
                            else:
                                action_score.append(ally.HP/2 * final_multiplier * target_multiplier)
                            
                    #Enemy Debuff
                    elif action.target_type == 'Enemy':
                        final_multiplier *= self.modifiers['debuff_favor']
                        for enemy in enemy_team:
                            target_multiplier = self.target_modifiers[enemy.AI_type]
                            if action.attempt.effect.condition.name in [condition.name for condition in enemy.conditions] and action.attempt.effect.condition.duration>1:
                                if action.resource_cost:
                                    action_score.append(-999)
                                else:
                                    action_score.append(0)
                            else:
                                action_score.append(enemy.HP/2 * final_multiplier * target_multiplier)
                
                combo_score.append(action_score)
            final_scores.append(combo_score)
        return final_scores
            