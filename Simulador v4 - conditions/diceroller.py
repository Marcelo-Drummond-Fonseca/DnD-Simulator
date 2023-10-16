import random

def d20roll(modifier=0, advantage = 0):
    roll = random.randint(1,20)
    if advantage != 0:
        roll2 = random.randint(1,20)
        print('Rolou',roll,'e',roll2,'no dado com', 'advantage' if advantage==1 else 'disadvantage','e tem modifier',modifier)
        if advantage == -1:
            roll = min(roll,roll2)
        elif advantage == 1:
            roll = max(roll,roll2)
    else:
        print('Rolou',roll,'no dado e tem modifier',modifier)
    return roll + modifier
    
def diceroll(amount=1, size=6, modifier=0):
    rolltotal = modifier
    roll_list = []
    for i in range(amount):
        roll = random.randint(1,size)
        roll_list.append(roll)
        rolltotal += roll
    print('Rolou',roll_list,'no dado e tem modifier',modifier)
    return rolltotal
    
#print(d20roll(), d20roll(-1), d20roll(1))
#print(diceroll(4,6,5), diceroll(2,12,6), diceroll(8,8))