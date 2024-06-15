import action as act

class Intelligence:

    def __init__(self, public_knowledge):
        self.public_knowledge = public_knowledge
        
    

    def choose_action(self, combo_list,allied_team,enemy_team, creature):
        final_scores = []
        for combo in combo_list:
            combo_score = []
            for action in combo:
                action_score = []
                #Pure Damage
                if isinstance(action.attempt.effect, act.Damage):
                    for enemy in enemy_team:
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
                                    if enemy.damage_type_multipliers.get(action.attempt.effect.damage[i][3]):
                                        avg_damage[i] = avg_damage[i]*enemy.damage_type_multipliers.get(action.attempt.effect.damage[i][3])
                        elif isinstance(action.attempt, act.Saving_Throw):
                            avg_half_damage = [(d[0]/2)*((d[1]+1)/2)+d[2] for d in action.attempt.effect.damage]
                            save_type = action.attempt.save_type
                            advantage = int(enemy.save_advantage[save_type]) - int(enemy.save_disadvantage[save_type])
                            if self.public_knowledge == False:
                                if advantage == 1: avg_damage = [damage*0.75 for damage in avg_damage]
                                elif advantage == -1: avg_damage = [damage*1.25 for damage in avg_damage]
                            else:
                                for i in range(len(avg_damage)):
                                    hit_chance = (max(0,20 - (action.attempt.save_DC - enemy.saving_throws[save_type]) - 1 - (advantage*4)))/20
                                    avg_damage[i] = avg_damage[i]*hit_chance + avg_half_damage*(1-hit-chance)
                                    if enemy.damage_type_multipliers.get(action.attempt.effect.damage[i][3]):
                                        avg_damage[i] = avg_damage[i]*enemy.damage_type_multipliers.get(action.attempt.effect.damage[i][3])
                        total_avg_damage = sum(avg_damage)
                        action_score.append(total_avg_damage)
                        
                #Pure Healing
                elif isinstance(action.attempt.effect, act.Healing):
                    for ally in allied_team:
                        avg_healing = action.attempt.effect.healing_die_amount*action.attempt.effect.healing_die_size+action.attempt.effect.healing_modifier
                        #if ally.MHP - ally.HP < avg_healing:
                        #    avg_healing = 0
                        avg_healing = min(avg_healing, ally.MHP - ally.HP)
                        action_score.append(avg_healing)
                        
                #Condition
                elif isinstance(action.attempt.effect, act.Apply_Condition):
                    #Self-Buff
                    if action.target_type == 'Self':
                        if action.attempt.effect.condition in creature.conditions:
                            action_score.append(0)
                        else:
                            action_score.append(25)
                    
                    #Ally Buff
                    elif action.target_type == 'Ally':
                        for ally in allied_team:
                            if action.attempt.effect.condition in ally.conditions:
                                action_score.append(0)
                            else:
                                action_score.append(25)
                            
                    #Enemy Debuff
                    elif action.target_type == 'Enemy':
                        for enemy in enemy_team:
                            if action.attempt.effect.condition in enemy.conditions:
                                action_score.append(0)
                            else:
                                action_score.append(25)
                
                combo_score.append(action_score)
            final_scores.append(combo_score)
        return final_scores
            