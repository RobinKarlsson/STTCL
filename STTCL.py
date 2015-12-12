import cPickle as pickle

class PlanetaryInstallation:
    def __init__(self, name, PIType):
        '''
        name:           string, name of PI
        PIType:         string, type of PI (eg. 960, open, <1600)
        '''
        self.name = name
        self.PIType = PIType

    def get_name(self):
        return self.name
    def get_type(self):
        return self.PIType

class STTCLGroup:
    def __init__(self, name, PI):
        '''
        name:       string, name of group
        PI:         list of PlanetaryInstallations objects
        '''
        self.name = name
        self.PI = PI

        self.completedGames = []
        self.ongoingGames = []
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.winratio = 0
        self.availableAttack = 2
        self.availableDefense = 2

    def defend(self, link):
        '''
        link:       match url
        '''
        if self.availableDefense > 0 and not link in self.ongoingGames and not link in self.completedGames:
            self.availableDefense -= 1
            self.ongoingGames.append(link)

    def attack(self, link):
        '''
        link:       match url
        '''
        if self.availableAttack > 0 and not link in self.ongoingGames and not link in self.completedGames:
            self.availableAttack -= 1
            self.ongoingGames.append(link)

    def gameCompleted(self, link, result, PI, role):
        '''
        link:       match url
        result:     string Won, Lost or Draw
        PI:         name of PI being challenged
        role:       string Attacker or Defender
        '''
        if link in self.completedGames or not link in self.ongoingGames:
            return

        self.ongoingGames.remove(link)
        self.completedGames.append(link)

        if result == "Won":
            self.wins += 1

            if role == "Attacker":
                self.availableAttack += 1
                self.PI.append(PI)
            else:
                self.availableDefense += 1

        elif result == "Lost":
            self.losses += 1

            if role == "Defender":
                self.PI.remove(PI)
                self.availableDefense += 1
            else:
                self.availableAttack += 1

        else:
            self.draws += 1

            if role == "Attacker":
                self.availableAttack += 1
            else:
                self.availableDefense += 1

        updateWinRatio()

    def updateWinRatio(self):
        self.winratio = (self.wins + self.losses + self.draws) / (self.wins * 1.0)

    def get_name(self):
        return self.name
    def get_PIList(self):
        self.PI
    def get_completedGames(self):
        return self.completedGames
    def get_ongoingGames(self):
        return self.ongoingGames
    def get_wins(self):
        return self.wins
    def get_losses(self):
        return self.losses
    def get_draws(self):
        return self.draws
    def get_winratio(self):
        return self.winratio
    def get_availableAttacks(self):
        return self.availableAttack
    def get_availableDefenses(self):
        return self.availableDefense


def saveObjects(objects, filename):
    '''
    save objects to filename
    '''
    with open(filename, 'wb') as tmp:
        pickle.dump(objects, tmp, -1)
            
def loadObjects(filename):
    '''
    return pickled objects from filename
    '''
    with open(filename, 'rb') as tmp:
        return pickle.load(tmp)
