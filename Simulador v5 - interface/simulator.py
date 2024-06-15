class Simulator:
    acting_order = []
    team1 = []
    team2 = []
    rounds = 0
    scores = []
    advantage_record = []
    deaths = []

    def __new__(cls):
        if not hasattr(cls, 'instance'):
          cls.instance = super(Simulator, cls).__new__(cls)
        return cls.instance
    
    def start_simulation(self,team1,team2):
        iniciative = []
        self.team1 = team1
        self.team2 = team2
        self.acting_order = []
        self.rounds = 0
        self.scores = []
        self.advantage_record = []
        self.deaths = []
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
            if i == 0:
                self.rounds += 1
                team1score = sum(creature.HP for creature in self.team1)
                team2score = sum(creature.HP for creature in self.team2)
                self.scores.append([team1score,team2score])
                self.advantage_record.append(1 if team1score>team2score else 2)
            active_creature = self.acting_order[i]
            if active_creature.is_alive():
                active_creature.start_of_turn()
            i = (i+1) % len(self.acting_order)
        return(self.end_simulation())
        
    def end_simulation(self):
        if self.team1:
            print('\nTeam 1 Wins!\n')
            response = {
                'winner': 1,
                'rounds': self.rounds,
                'advantage_record': self.advantage_record,
                'scores': self.scores,
                'deaths': self.deaths
            }
            return(1)
        elif self.team2:
            print('\nTeam 2 Wins!\n')
            response = {
                'winner': 2,
                'rounds': self.rounds,
                'advantage_record': self.advantage_record
                'scores': self.scores
                'deaths': self.deaths
            }
            
    def notify_death(self,creature,team):
        deaths.append(creature.name)
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
            
    def get_allied_team(self,team):
        if team == 1:
            return self.team1
        elif team == 2:
            return self.team2