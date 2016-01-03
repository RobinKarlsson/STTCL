import os

def createFolders(folder):
    '''
    create folder if missing
    input: string
    '''
    if not os.path.exists(folder):
        os.makedirs(folder)

def writeTxt(filename, txt):
    '''
    write text to a file in the HTML directory
    input: strings filename, txt
    '''
    filename = "HTML/" + filename
    with open(filename, "wb") as tmp:
        tmp.write(txt)



def get_victor(tm):
    tm_res = tm.get_result()

    if not tm_res == "draw" and not tm_res == "ongoing":
        return "Victor: %s" %tm_res[1]
    return tm_res
    
def get_availability(pi):
    return "available" if pi.get_status() else "unavailable"


def writeSeasons(grouplst, PIlst, TMlst):
    '''
    generate season html document
    input: list of group objects, list of PI objects, list of tm objects
    '''
    #create list of tuples where first element of tuple is name of group, 2nd is a list of groups PI objects where 1st element is PI name, 2nd PI type (960, u1600, open), 3d whether PI is available for challenge
    participants = [[group.get_name(), [[pi.get_name(), pi.get_type(), get_availability(pi)] for pi in group.get_PIList()], group.get_availableAttacks(), group.get_availableDefenses()] for group in grouplst]

    participantsHTML = []

    #generate html string for participating groups and store string in participantsHTML
    for participant in participants:
        assets = " | ".join(["%s (%s), %s" %(pi[0], pi[1], pi[2]) for pi in participant[1]])
        participantsHTML.append('<tr><td><p class="Group">%s</p></td><td><p class="text">%s</p></td><td><p class="text">%s</p></td><td><p class="PI">%s</p></td></tr>' %(participant[0], participant[2], participant[3], assets))

    participantsHTML = "\n".join(participantsHTML)





    #generate string of TM data for each TM object in TMlst
    tmHTML = "\n".join(['<tr><td><p class="text">%s</p></td><td><p class="text">%s</p></td><td><p class="text">%s</p></td><td><p class="text">%s</p></td><td><p class="text">%s</p></td><td><p class="text">%s</p></td><td><p class="text">%s</p></td></tr>' %(tm.get_attacker(), tm.get_defender(), tm.get_PIname(), tm.get_Players(), tm.get_Standing(), get_victor(tm), tm.get_TMlink()) for tm in TMlst])

    seasonHTML = """
    <html>
	<head>
		<meta charset="utf-8">
		<meta http-equiv='cache-control' content='no-cache'>
		<meta http-equiv='expires' content='-1'>
		<link type="text/css" rel="stylesheet" href="../css/season.css">
	</head>
	
	<sec>
		<h1 class="title">Participants</h1><br>
		<table class="sec">
			<tr><td><p class="sub_title">Group</p></td><td><p class="sub_title">Attacks</p></td><td><p class="sub_title">Defences</p></td><td><p class="sub_title">Planetary Installations</p></td></tr>
			%s
		</table>
	</sec><br><br><br><br><br><br>

	<sec>
		<h1 class="title">Matches</h1><br>
		<table class="sec">
			<tr><td><p class="sub_title">Attacker</p></td><td><p class="sub_title">Defender</p></td><td><p class="sub_title">Planetary Installation</p></td><td><p class="sub_title">Players</p></td><td><p class="sub_title">Score</p></td><td><p class="sub_title">Result</p></td><td><p class="sub_title">Matchlink</p></td></tr>
			%s
		</table>
	</sec>
    </html>
    """ %(participantsHTML, tmHTML)

    writeTxt("Seasons/2016.html", seasonHTML)

def writePI(PIlst):
    '''
    generate PI html document
    input: list of PI objects
    '''


def writeGroup(grouplst):
    '''
    generate group html document
    input: list of group objects
    '''


def writeIndex():
    '''
    generate index html document
    '''
    index = """
    <!DOCTYPE html>

    <html>
            <head>
                    <meta charset="utf-8">
                    <meta http-equiv='cache-control' content='no-cache'>
                    <meta http-equiv='expires' content='-1'>
                    <title>STTCL</title>
                    <link type="text/css" rel="stylesheet" href="css/global.css">
                    <script type="text/javascript" src="js/nav.js"></script>
                    <body onload="load_2016();">
            </head>
            
            <maintable>
                    <tablerows>
                            <nav>
                                    <p class="text">Seasons</p>
                                    <li><a href ="#" onclick="load_2016()"> 2016 </a></li>
                            </nav>

                            <iframe id ="ContFrame" frameBorder="0" border="0" onload="resize('Content')">oh no, it looks like your browser might not be compatible!</iframe>
                    </tablerows>
            </maintable>
    </html>
    """

    writeTxt("index.html", index)



def writeHTML(grouplst, PIlst, TMlst):
    '''
    generate html documents
    input: list of group objects, list of PI objects, list of tm objects
    '''
    writeIndex()
    writeSeasons(grouplst, PIlst, TMlst)
    writePI(PIlst)
    writeGroup(grouplst)



def writeJS():
    '''
    generate js documents
    '''
    navjs = """
    function load_2016(){
	document.getElementById("ContFrame").src = "Seasons/2016.html";
	reset_size("ContFrame");
    }

    function reset_size(id) {
            var doc = document.getElementById(id);
            doc.height = screen.height / 1.3;
            doc.width = screen.width / 1.25;
    }

    function resize(id) {
            var doc = document.getElementById(id);
            var body_ = doc.contentWindow.document.body;
            var html_ = doc.contentWindow.document.documentElement;

            doc.height = Math.max(body_.scrollHeight, body_.offsetHeight, html_.clientHeight, html_.scrollHeight, html_.offsetHeight);
            doc.width = Math.max(body_.scrollWidth, body_.offsetWidth, html_.clientWidth, html_.scrollWidth, html_.offsetWidth);
    }
    """


    writeTxt("js/nav.js", navjs)



def writeCSS():
    '''
    generate css documents
    '''
    globalcss = """
    body {
	background-color: #DFDFFF;
    }

    maintable {
            display: table;
            border-spacing: 10px;
    }
    tablerows {
            display: table-row;
    }
    nav {
            display: table-cell;
            color: red;
            width: 20%;
            padding: 15px;
            vertical-align: top;
    }
    nav li {
            list-style-type: none;
            padding: 5px 10px 5px 10px;
    }
    nav li a:link {
            border-bottom: none;
            font-weight: bold;
    }
    nav li a:hover {
            color: #CFCFFA;
            opacity: 0.7;
    }

    iframe#ContFrame {
            display: table;
    }
    """



    seasoncss = """
    sec h1.title {
	text-align: center;
    }

    sec table.sec {
            border-collapse: separate;
            border-spacing: 10px;
    }

    sec table.sec td {
            margin: 0px 10px 10px 10px;
            padding: 0px 10px 10px 10px;
    }

    sec p {
            font-weight: normal;
            text-align: left;
    }
    sec p.sub_title {
            font-weight: bold;
    }
    sec p.text {
    }
    sec p.Group {
    }
    sec p.PI {
            font-weight: italic;
    }
    """

    writeTxt("css/global.css", globalcss)
    writeTxt("css/season.css", globalcss)



def writeData(grouplst = [], PIlst = [], TMlst = []):
    '''
    main function, creates necessary folders and generate documents
    input: list of group objects, list of PI objects, list of tm objects
    '''
    #needed folders
    folders = ["HTML", "HTML/css", "HTML/js", "HTML/Seasons"]

    #create any missing folders
    for f in folders:
        createFolders(f)


    writeCSS()
    writeJS()
    writeHTML(grouplst, PIlst, TMlst)
