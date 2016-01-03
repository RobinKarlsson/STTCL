import mechanize
import sys
from bs4 import BeautifulSoup

def initmec():
    '''
    initialize mechanize browser object
    output: mechanize browser object
    '''
    browser = mechanize.Browser()
    browser.set_handle_equiv(True)
    browser.set_handle_redirect(True)
    browser.set_handle_gzip(False)
    browser.set_handle_referer(True)
    browser.set_handle_refresh(True)
    browser.set_handle_robots(False)
    browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    return browser

def mecopner(browser, link):
    '''
    load a page through mechanize
    input: browser object, string link to load
    output: BeautifulSoup object of the page
    '''
    while True:
        try:
            response = browser.open(link, timeout = 12.0)
            return BeautifulSoup(response, "lxml")

        except Exception, errormsg:
            print repr(errormsg)
            print "something went wrong, reopening '%s'" %link




def getTMList(link, browser = initmec()):
    '''
    build a list of tm objects from links in a public chess.com forum
    input: string url, browser object
    output: list of TM objects
    '''
    ""
    #list to store TM objects in
    TMlist = []

    #if chess.com ever fix the 100 pages bug, change the for loop to "while True"
    for i in range(1, 101):
        #create soap object of forum page
        soup = mecopner(browser, "%s?page=%i" %(link, i))

        #for each post
        for note in soup.find_all(class_ = "user-content"):

            #for each word in post
            for word in note.text.split():
                #if word is a tm link and not a duplicate post
                if word.startswith("http://www.chess.com/groups/team_match?id=") and word not in [tm.get_TMlink() for tm in TMlist]:
                    #create a TM object
                    tm = TM(word, mecopner(browser, word))

                    #if match name starts with sttcl
                    if tm.get_TMname()[0:5].lower() == "sttcl":
                        #add TM object to TMlist
                        TMlist.append(tm)
                    else:
                        print "%s on %s?page=%i isnt a sttcl match" %(tm.get_TMlink(), link, i)

        #if there arent a next page button
        if not soup.find_all(class_ = "next-on"):
            #exit loop
            break

    #return list of TM objects
    return TMlist

class TM:
    '''
    Team Match (TM) object
    '''
    def __init__(self, link, soup = None):
        '''
        initialize object
        input: string link to team match, BeautifulSoup object of match page
        '''
        #link to tm
        self.link = link

        if not soup:
            #looks like we will have to cook our own soup
            soup = mecopner(initmec(), self.link)

        #match name
        self.TMname = soup.find(class_ = "page-title").text.strip()

        #match name MUST be of the format 'STTCL: ATTACKING_GROUP attacks PI_NAME'
        #ie. match name MUST start with 'STTCL:' followed by attackers name, the word ' attacks ' followed by, and ending with, PI name!!!
        self.attackinggroup, self.attackedPI = self.TMname.lower().split("sttcl:")[1].split(" attacks ")

        #call objects update function
        self.update(soup)

    def update(self, soup = None):
        '''
        update object
        input: BeautifulSoup object of match page
        '''
        if not soup:
            #looks like we will have to cook our own soup
            soup = mecopner(initmec(), self.link)

        #create list where the first 2 objects are the participating groups names and 3d object points/team
        groups = [x.strip() for x in soup.find(class_ = "default border-top alternate").text.replace(u'\xa0', u' ').strip().split("\n")[1:] if x.strip() != ""]
        self.team1 = groups[0].lower()
        self.team2 = groups[1].lower()

        #define attacker/defender
        if self.attackinggroup != self.team1 and self.attackinggroup != self.team2:
            if self.attackinggroup in self.team1 and not self.attackinggroup in self.team2 and not self.team2 in self.attackinggroup:
                self.attackinggroup = self.team1
                self.defendinggroup = self.team2
            elif self.attackinggroup in self.team2 and not self.attackinggroup in self.team1 and not self.team1 in self.attackinggroup:
                self.attackinggroup = self.team2
                self.defendinggroup = self.team1

            elif self.team1 in self.attackinggroup and not self.attackinggroup in self.team2 and not self.team2 in self.attackinggroup:
                self.attackinggroup = self.team1
                self.defendinggroup = self.team2
            elif self.team2 in self.attackinggroup and not self.attackinggroup in self.team1 and not self.team1 in self.attackinggroup:
                self.attackinggroup = self.team2
                self.defendinggroup = self.team1

            else:
                print "couldnt find attacking group (%s)!!!" %self.link
                sys.exit()

        else:
            if self.attackinggroup == self.team1:
                self.defendinggroup = self.team2
            else:
                self.defendinggroup = self.team1

        #create list of points per team
        points = groups[2].split("=")[1:]
        try:
            self.points_team1 = int(points[0])
            self.points_team2 = int(points[1])
        #match hasnt started yet
        except IndexError:
            self.points_team1 = 0
            self.points_team2 = 0

        #match info
        tmp = soup.find(class_ = "simple border-top clearfix alternate").text.split("\n")
        self.players = 0
        for i in range(len(tmp)):
            x = tmp[i].strip()

            if x != "":
                if x == "Game Type:":
                    self.gametype = tmp[i+1]

                    if self.gametype == "Chess960":
                        self.gametype == "960"

                elif x == "Registration Open:":
                    self.regopendate = dateFormat(tmp[i+1])

                elif x == "Players Per Team:":
                    self.players = int(tmp[i+1])

                elif x == "Rating Range:":
                    self.ratingrange = tmp[i+1]

    def __eq__(self, other):
        '''
        compare with other objects
        other:      TM object
        '''
        return self.link == other.get_TMlink()

    def get_result(self):
        '''
        get result of match
        output:     if match has a winner, list where the 2nd element is the matchs winner and 4th element loser
                    else string ongoing or draw
        '''

        #total number of points available
        totpoints = self.players * 2
        #points remaining
        pointsremain = totpoints - self.points_team1 - self.points_team2

        #provisional win, PW
        PW = False

        #if enough points has been accumulated for a provisional win, set PW to true
        if self.points_team1 > self.points_team2 + pointsremain or self.points_team2 > self.points_team1 + pointsremain:
            PW = True

        #if match completed or we have a provisioal win
        if pointsremain == 0 or PW:
            #if team1 has the most points
            if self.points_team1 > self.points_team2:
                return ["won", self.team1, "lost", self.team2]
            #if team2 has the most points
            elif self.points_team1 < self.points_team2:
                return ["won", self.team2, "lost", self.team1]
            #if neither of above statements were true, we have a draw
            else:
                return "draw"

        #if we reach this far, the match is still undecided
        return "ongoing"

    def get_TMname(self):
        return self.TMname
    def get_TMlink(self):
        return self.link
    def get_GameType(self):
        return self.gametype
    def get_RegistrationOpenDate(self):
        return self.regopendate
    def get_Players(self):
        return self.players
    def get_RatingRange(self):
        return self.ratingrange
    def get_Standing(self):
        tmp = {self.team1: self.points_team1, self.team2: self.points_team2}
        return "%i x %i" %(tmp[self.attackinggroup], tmp[self.defendinggroup])
    def get_attacker(self):
        return self.attackinggroup
    def get_defender(self):
        return self.defendinggroup
    def get_teams(self):
        return [self.team1, self.team2]
    def get_PIname(self):
        return self.attackedPI
    def get_TotalNumberPoints(self):
        return self.players * 2
    def get_PointsRemaining(self):
        return self.get_TotalNumberPoints() - self.points_team1 - self.points_team2

def dateFormat(date):
    '''
    takes a date in the format "Jun 4, 2015"
    returns list of integers [year, month, day]
    '''
    date = date.replace("Jan", "01").replace("Feb", "02").replace("Mar", "03").replace("Apr", "04").replace("May", "05").replace("Jun", "06").replace("Jul", "07").replace("Aug", "08").replace("Sep", "09").replace("Oct", "10").replace("Nov", "11").replace("Dec", "12").replace(",", "").split(" ")
    return [int(date[2]), int(date[0]), int(date[1])]
