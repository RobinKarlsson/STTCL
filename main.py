import os
import cPickle as pickle
from scrapper import *
from htmlGenerator import writeData

#create data directory if it doesnt already exist
if not os.path.exists("data"):
    os.makedirs("data")



class PlanetaryInstallation:
    '''
    PI object
    '''
    def __init__(self, name, PIType):
        '''
        Initialize PI object
        name:           string, name of PI
        PIType:         string, type of PI (eg. 960, open, u1600)
        owner:          STTCLGroup object
        '''
        #PI name
        self.name = name.lower().strip()
        #pi type, eg "960", "u1600", "open"
        self.PIType = PIType.strip()
        #tm history
        self.history = []

        # True = available for attack, False unavailable for attack
        self.status = True

    def __eq__(self, other):
        '''
        compare with other objects
        other:      PlanetaryInstallation object
        '''
        return self.name == other.get_name()

    def get_name(self):
        return self.name
    def get_type(self):
        return self.PIType

    def set_owner(self, group):
        '''
        change PI owner
        input: STTCLGroup object
        '''
        self.owner = group
    def add_history(self, group, tm, happening):
        '''
        add a tm to PIs history
        input: STTCLGroup object, TM object, string describing what happened
        '''
        self.history.insert(0, [group, tm, happening])
    def get_owner(self):
        return self.owner

    def get_status(self):
        return self.status
    def set_unavailable(self):
        self.status = False
    def set_available(self):
        self.status = True
    

class STTCLGroup:
    '''
    STTCL group object
    '''
    def __init__(self, name, link, PI):
        '''
        Initialize object
        name:       string, name of group
        name:       string, link to group
        PI:         list of PlanetaryInstallation objects
        '''
        self.name = name.lower()
        self.PI = PI
        self.link = link

        #history of completed games
        self.completedGames = []
        #currently ongoing games
        self.ongoingGames = []
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.winratio = 0

        #each group has 2 attacks and 2 defences available
        self.availableAttack = 2
        self.availableDefense = 2

    def addTM(self, tm):
        '''
        tm:     TM object
        '''
        #tm result
        result = tm.get_result()
        #attacking team name, string
        attacker = tm.get_attacker()
        newgame = True

        #make PI_challenged point to the right PI object
        PI_challenged = tm.get_PIname()
        for pi in loadObjects("data/PI.obj"):
            if pi.get_name() == PI_challenged:
                PI_challenged = pi
                break

        #if not a new game
        if tm in self.completedGames or tm in self.ongoingGames:
            print "updating %s for %s" %(tm.get_TMlink(), self.name)
            newgame = False

            #make tm point to the right TM object
            if tm in self.completedGames:
                for match in self.completedGames:
                    if tm == match:
                        tm = match
                        break
            elif tm in self.ongoingGames:
                for match in self.ongoingGames:
                    if tm == match:
                        tm = match
                        break
            else:
                raise Exception("Couldnt find tm")

            #update tm data
            tm.update()

        #if the challenged PI isnt available for new challenges
        if newgame and not PI_challenged.get_status():
            print "%s is not available for challenge, %s" %(PI_challenged.get_name(), tm.get_TMlink())
            return

        #if we are the attacker
        if attacker == self.name:
            role = "Attacker"
            #if it's a new game, verify that we have attacks available
            if newgame:
                if not self.attack(tm):
                    print "%s does not have any available attacks, %s" %(self.name, tm.get_TMlink())
                    return

        #if we are the defender
        else:
            role = "Defender"
            if newgame:
                #verify we have defences available
                if not self.defend(tm):
                    print "%s does not have any available defences, %s" %(self.name, tm.get_TMlink())
                    return

        #if the result of the tm hasnt been decided yet
        if result == "ongoing":
            #make PI unavailable for other challenges
            PI_challenged.set_unavailable()

        #if we won
        elif self.name == result[1]:
            result = "Won"
        #if we lost
        elif self.name == result[3]:
            result = "Lost"
        #looks like it was a draw
        else:
            result = "Draw"

        #if the game is over and hasnt already been processed
        if result != "ongoing" and not tm in self.completedGames:
                self.gameCompleted(tm, result, role)

    def defend(self, tm):
        '''
        input:      TM object
        output:     bool
        '''
        #if we have defence spots available
        if self.availableDefense > 0:
            #reduce available spots with 1
            self.availableDefense -= 1
            #add tm to ongoing games list
            self.ongoingGames.append(tm)

        else:
            return False
        return True

    def attack(self, tm):
        '''
        input:      TM object
        output:     bool
        '''
        #if we have attack spots available
        if self.availableAttack > 0:
            #reduce available spots with 1
            self.availableAttack -= 1
            #add tm to ongoing games list
            self.ongoingGames.append(tm)

        else:
            return False
        return True

    def gameCompleted(self, tm, result, role):
        '''
        tm:         TM object
        link:       match url
        result:     string Won, Lost or Draw
        role:       string Attacker or Defender
        '''
        #string, name of challenged PI
        PIchallenged = tm.get_PIname()
        #list of existing PI objects
        PIs = loadObjects("data/PI.obj")

        #make PIchallenged point to the right PI object
        for pi in PIs:
            if pi.get_name() == PIchallenged:
                PIchallenged = pi
                break

        #remove tm from ongoing game
        self.ongoingGames.remove(tm)
        #add tm to completed games
        self.completedGames.append(tm)

        #set challenged PI to available for attack
        PIchallenged.set_available()

        #if we won
        if result == "Won":
            #add 1 to number of wins
            self.wins += 1

            #if we were the attacking party
            if role == "Attacker":
                #restore 1 attack slot
                self.availableAttack += 1
                #add PIchallenged to our list of owned PI objects
                self.PI.append(PIchallenged)
                #set PIchallenged owner to us
                PIchallenged.set_owner(self)
                #add match to PIchallenged history list
                PIchallenged.add_history(self, tm, "conquered by %s" %self.name)

            #if we were the defending party
            else:
                #restore 1 defence slot
                self.availableDefense += 1
                #add match to PIchallenged history list
                PIchallenged.add_history(self, tm, "defended by %s" %self.name)

            #save PI list
            saveObjects(PIs, "data/PI.obj")

        #if we lost
        elif result == "Lost":
            #add 1 to number of losses
            self.losses += 1

            #if we were the defending party
            if role == "Defender":
                #remove PIchallenged from our list of PIs
                self.PI.remove(PIchallenged)
                #restore 1 defence slot
                self.availableDefense += 1

            #if we were the attacker
            else:
                #restore 1 attack slot
                self.availableAttack += 1

        #if draw
        else:
            #add 1 to number of draws
            self.draws += 1

            #if we were the attacker
            if role == "Attacker":
                #restore 1 attack slot
                self.availableAttack += 1
            #if we were the defender
            else:
                #restore 1 defence slot
                self.availableDefense += 1
                #add match to PIchallenged history list
                PIchallenged.add_history(self, tm, "defended by %s" %self.name)
                #save PI objects
                saveObjects(PIs, "data/PI.obj")

        #update groups winratio
        self.updateWinRatio()

    def __eq__(self, other):
        '''
        compare with other objects
        other:      STTCLGroup object
        '''
        return self.name == other.get_name()

    def updateWinRatio(self):
        '''
        update groups winratio
        '''
        if self.wins != 0:
            self.winratio = (self.wins + self.losses + self.draws) / (self.wins * 1.0)
        else:
            self.winratio = 0.00

    def get_name(self):
        return self.name
    def get_link(self):
        return self.link
    def get_PIList(self):
        return self.PI
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
    try:
        with open(filename, 'rb') as tmp:
            pickled = pickle.load(tmp)
            if pickled == "":
                return []
            return pickled
    except IOError:
        saveObjects("", filename)
        return []








def addGroup():
    groupname = raw_input("\ngroup name: ")
    grouplink = raw_input("group link: ")
    groupassets = raw_input("comma seperated list of planetary installations owned by %s: " %groupname)

    #list of existing PI objects
    current_PIs = loadObjects("data/PI.obj")
    #listfor storing new PIs
    PIlst = []

    #for each new PI
    for pi in groupassets.split(","):
        pi_type = ""
        pi = pi.strip()

        while pi_type not in ['open', 'u1600', '960']:
            pi_type = raw_input("\nset PI type for %s (available types are 'open', 'u1600', '960'): " %pi)

        #create PI object
        new_pi = PlanetaryInstallation(pi, pi_type)

        #if the newly created PI already exists, abort
        if new_pi in current_PIs:
            for existing_pi in current_PIs:
                if existing_pi.get_name() == pi:
                    print "%s is already an existing PI, owned by %s!!! aborting" %(pi, existing_pi.get_owner().get_name())
                    return

        #add new_pi to list of new PI objects
        PIlst.append(new_pi)

    #create STTCLGroup object
    group = STTCLGroup(groupname, grouplink, PIlst)

    #list of current STTCLGroup objects
    current_groups = loadObjects("data/groups.obj")

    #if not a duplicate group
    if group not in current_groups:

        #for each new PI, set its owner to the new STTCLGroup
        for pi in PIlst:
            pi.set_owner(group)

        #add the newly created group to list of existing groups
        current_groups.append(group)
        #save list of existing groups
        saveObjects(current_groups, "data/groups.obj")
        #save list of PIs
        saveObjects(current_PIs + PIlst, "data/PI.obj")
    else:
        print "%s already exists!!!" %groupname



def viewPIs():
    PIs = loadObjects("data/PI.obj")
    for pi in PIs:
        print "%s (%s) owned by %s" %(pi.get_name(), pi.get_type(), pi.get_owner().get_name())

def viewGroups():
    groups = loadObjects("data/groups.obj")

    for group in groups:
        print "\nGroup name: %s" %group.get_name()
        print "Group assets: %s" %" | ".join(["%s (%s)" %(pi.get_name(), pi.get_type()) for pi in group.get_PIList()])
        print "Group link: %s" %group.get_link()
        print "number wins: %s" %group.get_wins()
        print "number losses: %s" %group.get_losses()
        print "number draws: %s" %group.get_draws()
        print "winratio: %s" %group.get_winratio()
        print "available attacks: %s" %group.get_availableAttacks()
        print "available defenses: %s" %group.get_availableDefenses()

def loadTMs(link = "http://www.chess.com/groups/forumview/dummy-sttcl-test-forum"):
    '''
    get list of TM objects from match links posted in a public forum
    '''
    #create browser object
    br = initmec()
    #get list of TM objects from link
    TMlst = getTMList(link, br)

    #process TM objects
    for tm in TMlst:
        processTM(tm)

    return TMlst

def processTM(tm):
    '''
    tm:     TM object
    '''
    print "match name: %s" %tm.get_TMname()
    print "tm url: %s" %tm.get_TMlink()
    print "game type: %s" %tm.get_GameType()
    print "reg open: %s" %tm.get_RegistrationOpenDate()
    print "players: %s" %tm.get_Players()
    print "ratingrange: %s" %tm.get_RatingRange()
    print "standing: %s" %tm.get_Standing()
    print "attacker: %s" %tm.get_attacker()
    print "groups: %s" %tm.get_teams()
    print "PI: %s" %tm.get_PIname()
    print "matchpoints total: %s" %tm.get_TotalNumberPoints()
    print "matchpoints remain: %s" %tm.get_PointsRemaining()
    print "result: %s" %tm.get_result()
    print "\n"

    #list of STTCLGroup objects
    groups = loadObjects("data/groups.obj")

    #for each participant in tm
    for participant in tm.get_teams():
        #for each group STTCLGroup object
        for group in groups:
            #if participant is this STTCLGroup
            if group.get_name() == participant:
                #call groups addTM function
                group.addTM(tm)
                break

    #save the updated list of STTCLGroup objects
    saveObjects(groups, "data/groups.obj")





def main():
    while True:
        choice = raw_input("1. add group\n2. view groups\n3. view PIs\n4. load tm data\n5. load tm data and generate html\n")

        if choice == "1":
            addGroup()
        elif choice == "2":
            viewGroups()
        elif choice == "3":
            viewPIs()
        elif choice == "4":
            loadTMs()
        elif choice == "5":
            groups = loadObjects("data/groups.obj")
            PIs = loadObjects("data/PI.obj")
            writeData(groups, PIs, loadTMs())

        elif choice == "exit":
            return

if __name__ == "__main__":
    main()
