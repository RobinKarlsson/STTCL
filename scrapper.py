import mechanize
from bs4 import BeautifulSoup

def initmec():
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
    while True:
        try:
            response = browser.open(link, timeout = 12.0)
            return BeautifulSoup(response, "lxml")

        except Exception, errormsg:
            print repr(errormsg)
            print "something went wrong, reopening %s" %link
            time.sleep(1.5)




def getTMLinkList(link = "http://www.chess.com/groups/forumview/dummy-sttcl-test-forum", browser = initmec()):
    '''
    takes link to a open chess.com forum from which TM objects are constructed
    returns list of TM objects
    '''
    ""
    TMlist = []

    for i in range(1, 101):
        soup = mecopner(browser, "%s?page=%i" %(link, i))

        for note in soup.find_all(class_ = "user-content"):
            for word in note.text.split():
                if word.startswith("http://www.chess.com/groups/team_match?id=") and word not in TMlist:
                    TMlist.append(TM(word, mecopner(browser, word)))

        if not soup.find_all(class_ = "next-on"):
            break

    return TMlist

class TM:
    def __init__(self, link, soup = None):
        self.link = link
        if not soup:
            print "You really should send me some soup"
            soup = mecopner(initmec(), self.link)

        self.TMname = soup.find(class_ = "page-title").text

        #match name MUST be of the format 'STTCL: ATTACKING_GROUP attacks PI_NAME'
        #ie. match name MUST start with 'STTCL:' followed by attackers name, the word ' attack ' followed by, and ending with, PI name!!!
        self.attackinggroup, self.attackedPI = self.TMname.lower().split("sttcl:")[1].split(" attacks ")

        groups = [x.strip() for x in soup.find(class_ = "default border-top alternate").text.replace(u'\xa0', u' ').strip().split("\n")[1:] if x.strip() != ""]
        self.team1 = groups[0].lower()
        self.team2 = groups[1].lower()

        if self.attackinggroup != self.team1 and self.attackinggroup != self.team2:
            if self.attackinggroup in self.team1 and not self.attackinggroup in self.team2:
                self.attackinggroup = self.team1
            elif self.attackinggroup in self.team2 and not self.attackinggroup in self.team1:
                self.attackinggroup = self.team2

        points = groups[2].split(" = ")[1:]
        try:
            self.points_team1 = int(points[0])
            self.points_team2 = int(points[1])
        except IndexError:
            self.points_team1 = 0
            self.points_team2 = 0

        tmp = soup.find(class_ = "simple border-top clearfix alternate").text.split("\n")
        for i in range(len(tmp)):
            x = tmp[i].strip()

            if x != "":
                if x == "Game Type:":
                    self.gametype = tmp[i+1]

                elif x == "Registration Open:":
                    self.regopendate = dateFormat(tmp[i+1])

                elif x == "Players Per Team:":
                    self.players = int(tmp[i+1])

                elif x == "Started On:":
                    self.startdate = dateFormat(tmp[i+1])

                elif x == "Rating Range:":
                    self.ratingrange = tmp[i+1]

    def get_result(self):
        totpoints = self.players * 2
        pointsremain = totpoints - self.points_team1 - self.points_team2

        if pointsremain == 0:
            if self.points_team1 > self.points_team2:
                return ["won", self.team1, "lost", self.team2]
            elif self.points_team1 < self.points_team2:
                return ["won", self.team2, "lost", self.team1]
            else:
                return "draw"

        return "ongoing"

    def __eq__(self, other):
        '''
        compare with other objects
        other:      TM object
        '''
        return self.link == other.get_TMlink()

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
    def get_StartDate(self):
        return self.startdate
    def get_RatingRange(self):
        return self.ratingrange
    def get_Standing(self):
        return {self.team1: self.points_team1, self.team2: self.points_team2}
    def get_attacker(self):
        return self.attackinggroup
    def get_teams(self):
        return [self.team1, self.team2]
    def get_TotalNumberPoints(self):
        return self.players * 2
    def get_PointsRemaining(self):
        return self.players * 2 - self.points_team1 - self.points_team2

def dateFormat(date):
    '''
    takes a date in the format "Jun 4, 2015"
    returns list of integers [year, month, day]
    '''
    date = date.replace("Jan", "01").replace("Feb", "02").replace("Mar", "03").replace("Apr", "04").replace("May", "05").replace("Jun", "06").replace("Jul", "07").replace("Aug", "08").replace("Sep", "09").replace("Oct", "10").replace("Nov", "11").replace("Dec", "12").replace(",", "").split(" ")
    return [int(date[2]), int(date[0]), int(date[1])]
