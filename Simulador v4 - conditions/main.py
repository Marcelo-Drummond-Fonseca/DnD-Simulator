from creature import Creature
from simulator import Simulator
from action import Action, Attack_Roll, Auto_Apply, Saving_Throw, Damage, Healing, Apply_Condition
from conditions import Condition, Condition_Effect, Modified_Attack, Modified_Defense, Modified_Economy

Ares = Creature('Ares',27,18,[5,-1,4,3,1,-1],-1)
Oona = Creature('Oona',29,15,[4,5,2,-1,1,0],3)
#Dragon = Creature('Dragon',100,18,[3,3,3,3,3,3],0)

longsword = Action('Longsword',1,'Enemy',Attack_Roll(5,Damage(1,8,5,'Slashing')))
spear = Action('Spear',1,'Enemy',Attack_Roll(4,Damage(1,6,5,'Piercing',follow_effect = Damage(1,6,0,'Piercing'))))
Ares.add_action([longsword])
Oona.add_action([spear,spear])
Ares.add_bonus_action([Action('Second Wind',1,'Self',Auto_Apply(Healing(1,10,2)), resource_cost = ['Second Wind',1])])
Ares.add_resource('Second Wind',1,'Short Rest')
action_surge = Condition('Action Surge', 'End of Target Turn', 1, [Modified_Economy(action_modifier=1)])
Ares.add_free_action([Action('Action Surge',1,'Self',Auto_Apply(Apply_Condition(action_surge)), resource_cost = ['Action Surge',1])])
Ares.add_resource('Action Surge',1,'Long Rest')
rage = Condition('Rage', 'End of Target Turn', 10, [Modified_Attack(damage_bonus=2),Modified_Defense(save_advantage = [1,0,0,0,0,0], damage_type_multipliers = {'Slashing': 0.5, 'Piercing': 0.5, 'Bludgeoning': 0.5})])
Oona.add_bonus_action([Action('Rage',1,'Self',Auto_Apply(Apply_Condition(rage)), resource_cost = ['Rage',1])])
Oona.add_resource('Rage',1,'Long Rest')
#Oona.add_action([Action('Mass Cure Wounds',6,'Ally',Auto_Apply(Healing(1,8,1)),resource_cost = ['Spell Slot 5',1])])
#Oona.add_resource('Spell Slot 5',2,'Long Rest')
#Dragon.add_action([Action('Claw',1,'Enemy',Attack_Roll(5,Damage(2,4,3,'Slashing'))),Action('Bite',1,'Enemy',Attack_Roll(5,Damage(1,10,3,'Piercing')))])
#Dragon.add_action([Action('Fire Breath',4,'Enemy',Saving_Throw(15,'DEX',True,Damage(4,6,0,'Fire')), resource_cost = ['Breath',1])])
#Dragon.add_resource('Breath',1,'Recharge',recharge_number = 5)

simulator = Simulator()
Team1wins = 0
Team2wins = 0
n=1000
for i in range(n):
    print("Healing combatants")
    Ares.full_restore()
    Oona.full_restore()
    print('\n\n')
    #Dragon.HP = Dragon.MHP
    result = simulator.start_simulation([Ares],[Oona])
    if result == 1:
        Team1wins += 1
    elif result == 2:
        Team2wins += 1
        
print('Team 1 ganhou:', Team1wins*100/n,'% das lutas')
print('Team 2 ganhou:', Team2wins*100/n,'% das lutas')