import random

def d20roll(modifier=0, advantage = 0):
    roll = random.randint(1,20)
    if advantage != 0:
        roll2 = random.randint(1,20)
        if advantage == -1:
            roll = min(roll,roll2)
        elif advantage == 1:
            roll = max(roll,roll2)
            
    return roll + modifier
    
def diceroll(amount=1, size=6, modifier=0):
    rolltotal = modifier
    for i in range(amount):
        rolltotal += random.randint(1,size)
    return rolltotal
    
#print(d20roll(), d20roll(-1), d20roll(1))
#print(diceroll(4,6,5), diceroll(2,12,6), diceroll(8,8))