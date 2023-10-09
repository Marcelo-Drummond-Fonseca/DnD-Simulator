from diceroller import d20roll, diceroll

class Action:
    def __init__(self, name):
        self.name = name
    
    def act(self, target):
        pass
        
class Basic_Attack(Action):
    
    def __init__(self,name,attack_bonus,damage_die_amount,damage_die_size,damage_modifier):
        self.name = name
        self.attack_bonus = attack_bonus
        self.damage_die_amount = damage_die_amount
        self.damage_die_size = damage_die_size
        self.damage_modifier = damage_modifier
        self.advantage = 0

    def act(self,target):
        #roll attack
        attack_roll = d20roll(self.attack_bonus,self.advantage)
        if attack_roll == 20 + self.attack_bonus:
            print('Critico!')
            hit = True
            damage = diceroll(2*self.damage_die_amount,self.damage_die_size,self.damage_modifier)
            target.take_damage(damage)
        else:
            hit = target.check_hit(attack_roll)
            if hit == True:
                damage = diceroll(self.damage_die_amount,self.damage_die_size,self.damage_modifier)
                target.take_damage(damage)
            