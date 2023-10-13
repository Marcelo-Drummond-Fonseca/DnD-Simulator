from creature import Creature
from simulator import Simulator
from action import Action, Attack_Roll, Auto_Apply, Saving_Throw, Damage, Healing

Ares = Creature('Ares',34,17,[5,-1,4,3,1,-1],-1)
Oona = Creature('Oona',29,15,[4,5,2,-1,1,0],3)
Dragon = Creature('Dragon',100,18,[3,3,3,3,3,3],0)

longsword = Action('Longsword',1,'Enemy',Attack_Roll(5,Damage(1,8,5,'Slashing')))
spear = Action('Spear',1,'Enemy',Attack_Roll(5,Damage(1,6,5,'Piercing',follow_effect = Damage(1,6,0,'Piercing'))))
Ares.add_action([longsword,longsword])
Oona.add_action([spear,spear])
Ares.add_bonus_action([Action('Second Wind',1,'Self',Auto_Apply(Healing(1,10,2)), resource_cost = ['Second Wind',1])])
Ares.add_resource('Second Wind',1,'Short Rest')
Oona.add_action([Action('Mass Cure Wounds',6,'Ally',Auto_Apply(Healing(1,8,1)),resource_cost = ['Spell Slot 5',1])])
Oona.add_resource('Spell Slot 5',2,'Long Rest')
Dragon.add_action([Action('Claw',1,'Enemy',Attack_Roll(5,Damage(2,4,3,'Slashing'))),Action('Bite',1,'Enemy',Attack_Roll(5,Damage(1,10,3,'Piercing')))])
Dragon.add_action([Action('Fire Breath',4,'Enemy',Saving_Throw(15,'DEX',True,Damage(4,6,0,'Fire')), resource_cost = ['Breath',1])])
Dragon.add_resource('Breath',1,'Recharge',recharge_number = 5)

simulator = Simulator()
Team1wins = 0
Team2wins = 0
n=1
for i in range(n):
    Ares.HP = Ares.MHP
    Oona.HP = Oona.MHP
    Dragon.HP = Dragon.MHP
    result = simulator.start_simulation([Ares,Oona],[Dragon])
    if result == 1:
        Team1wins += 1
    elif result == 2:
        Team2wins += 1
        
print('Team 1 ganhou:', Team1wins*100/n,'% das lutas')
print('Team 2 ganhou:', Team2wins*100/n,'% das lutas')