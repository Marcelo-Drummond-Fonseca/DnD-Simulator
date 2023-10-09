class Simulator:
    acting_order = []
    team1 = []
    team2 = []

    def __new__(cls):
        if not hasattr(cls, 'instance'):
          cls.instance = super(Simulator, cls).__new__(cls)
        return cls.instance
        
    def start_simulation(self,team1,team2):
        iniciative = []
        self.team1 = team1
        self.team2 = team2
        for creature in team1:
            iniciative.append([creature.roll_iniciative(), creature])
            creature.add_simulator(self, 1)
        for creature in team2:
            iniciative.append([creature.roll_iniciative(), creature])
            creature.add_simulator(self, 2)
        iniciative.sort(key=lambda x: x[0], reverse=True)
        for iniciative_creature in iniciative:
            self.acting_order.append(iniciative_creature[1])
        return(self.simulation_loop())
        
    def simulation_loop(self):
        i = 0
        while(self.team1 and self.team2):
            active_creature = self.acting_order[i]
            if active_creature.is_alive():
                active_creature.take_turn()
            i = (i+1) % len(self.acting_order)
        return(self.end_simulation())
        
    def end_simulation(self):
        if self.team1:
            print('\nTeam 1 Wins!\n')
            return(1)
        elif self.team2:
            print('\nTeam 2 Wins!\n')
            return(2)
            
    def notify_death(self,creature,team):
        if team == 1:
            for i, o in enumerate(self.team1):
                if o.name == creature.name:
                    del self.team1[i]
                    break
        elif team == 2:
            for i, o in enumerate(self.team2):
                if o.name == creature.name:
                    del self.team2[i]
                    break
                    
    def get_enemy_team(self,team):
        if team == 1:
            return self.team2
        elif team == 2:
            return self.team1