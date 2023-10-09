from creature import Creature
from simulator import Simulator
from action import Action, Basic_Attack

Ares = Creature('Ares',34,17,-1)
Oona = Creature('Oona',29,15,3)

Ares.add_action(Basic_Attack('Longsword',5,1,8,5,'Slashing'))
Oona.add_action(Basic_Attack('Spear',5,2,6,5,'Piercing'))
Oona.add_damage_type_multiplier('Slashing',0.5)

simulator = Simulator()
Team1wins = 0
Team2wins = 0
n=1
for i in range(n):
    Ares.HP = Ares.MHP
    Oona.HP = Oona.MHP
    result = simulator.start_simulation([Ares],[Oona])
    if result == 1:
        Team1wins += 1
    elif result == 2:
        Team2wins += 1
        
print('Team 1 ganhou:', Team1wins*100/n,'% das lutas')
print('Team 2 ganhou:', Team2wins*100/n,'% das lutas')