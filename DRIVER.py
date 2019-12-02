import tweepy
from multiprocessing import Queue
import json
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
import threading
import curses
import curses.textpad
from sys import getsizeof
import warnings
warnings.filterwarnings('ignore')

reloadTimelines = False
reloadInteractions = False
reloadRetweets = False
reloadReplies = False
useSavedData = True

quitt = False

idQueue = Queue()
replyQueue = Queue()
analyzeQueue = Queue()
endQueue = Queue()
endNode:threading.Thread
save = {}
api = tweepy.API()
stats = {}

waiting = 0
timelineNodeA = 5
replyNodeA = 1
analyzeNodeA = 5

timelineNodes = []
replyNode = []
analyzeNode = []

tNodeStatus = [0] * timelineNodeA
rNodeStatus = [0] * replyNodeA
aNodeStatus = [0] * analyzeNodeA

exceptions = Queue()
Net = []
backupInfo = ["last whole update", "lastB backup update + size", "lastS statsbackup update + size", "backupnow", "back"]

path = os.path.abspath("phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
# options = webdriver.FirefoxOptions()
# options.add_argument('-headle
browser = webdriver.PhantomJS(executable_path=path)  # , firefox_options=options)

def initThreads():
    global endNode
    for x in range(0, timelineNodeA):
        timelineNodes.append(threading.Thread(target=timelineNodejob, daemon=True, args=[x]))
    for x in range(0, replyNodeA):
        replyNode.append(threading.Thread(target=replyNodejob,daemon=True,args=[x]))
    for x in range(0, analyzeNodeA):
        analyzeNode.append(threading.Thread(target=analyzeNodejob,daemon=True,args=[x]))
    endNode = threading.Thread(target= endNodeJob)

def init():
  global api
  global save
  consumer_key = "iTgGukoBAPecLL5awvC0b7jp7"
  consumer_secret = "2jXCBmYLBSubcXtCljbSP1eBfsUbeFgUlsclswt8tQ5Gn4DDXf"
  access_token = "1166697426318757888-QBNkGhVY8bqeycxRulTLYAiZrhnN1m"
  access_token_secret = "d0zLEPH8ZqNSePfyaZqIpCEHp7CfdJh04u7V3lscRh2ev"
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True)
init()

u1 = api.get_user(612473)
idQueue.put(u1.id)
u2 = api.get_user("FoxNews")
idQueue.put(u2.id)

def backupThread(x:int)->bool:
    while True:
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        successB = 0
        successS = 0
        try:
            with open("save.json", "w+") as json_filei:
                with open("backups/backup_" + dt_string + ".json", "w+") as json_file:
                    json.dump(save, json_file, indent=4)
                json.dump(save, json_filei, indent=4)
            backupInfo[1] = "lastB " + dt_string + " " + str(os.stat("backups/backup_" + dt_string + ".json").st_size)
            successB = 1
        except Exception as e:
            exceptions.put_nowait(e)
            #now = datetime.now()
            #print("Warning couldnt backup " + now.strftime("%d_%m_%Y_%H_%M_%S"))

        try:
            with open("stats.json", "w+") as json_filei:
                with open("statsbackups/statsbackup_" + dt_string + ".json", "w+") as json_file:
                    json.dump(stats, json_file, indent=4)
                backupInfo[2] = "lastS " + dt_string + " " + str(os.stat("statsbackups/statsbackup_" + dt_string + ".json").st_size)
                json.dump(stats, json_filei, indent=4)
            successS = 1
        except Exception as e:
            exceptions.put_nowait(e)
        if successB == 1 and successS == 1:
            backupInfo[0] = "LastWholeUpdate " + dt_string
        if x != 0:
            return successS == 1 and successB == 1
        time.sleep(600)


def timelineNodejob(x:int):
    global quitt
    global tNodeStatus
    ends = 0
    while not quitt:
        user = 0
        if ends == 10000:
            quitt = True
        while user == 0 and not quitt:
            try:
                user = idQueue.get_nowait()
            except:
                time.sleep(1)
        if not quitt:
            #print("got to Timeline " + str(user))
            try:
                getTimeline(user)
            except Exception as e:
                exceptions.put_nowait(e)
                #print("couldnt get Timeline " + str(user))
            ends += 1
    while not idQueue.empty():
        user = 0
        try:
            user = idQueue.get_nowait()
        except:
            time.sleep(1)
        if user != 0:
            try:
                getInfo(user)
            except Exception as e:
                #print("couldnt get info " + str(user))
                exceptions.put_nowait(e)
    tNodeStatus[x] = 1
    backupThread(30)
    #print("done with t " + str(x))

def replyNodejob(x:int):
    global quitt
    global rNodeStatus
    while 0 in tNodeStatus or not replyQueue.empty():
        user = 0
        while user == 0 and (0 in tNodeStatus or not replyQueue.empty()):
            try:
                user = replyQueue.get_nowait()
            except:
                time.sleep(1)
        #print("got to replies " + str(user))
        try:
            getReplies(user)
        except Exception as e:
            exceptions.put_nowait(e)
            #print("couldnt get replies " + str(user))
    rNodeStatus[x] = 1
    #print("done with r "+str(x))

def analyzeNodejob(x:int):
    global quitt
    global aNodeStatus
    while 0 in rNodeStatus or not analyzeQueue.empty():
        user = 0
        while user == 0 and (0 in rNodeStatus or not analyzeQueue.empty()):
            try:
                user = analyzeQueue.get_nowait()
            except:
                time.sleep(1)
        #print("got to analyze " + str(user))
        try:
            analyze(user)
        except Exception as e:
            exceptions.put_nowait(e)
            #print("could not analyze " + str(user))
    aNodeStatus[x] = 1
    #print("done with A " + str(x))

def endNodeJob():
    global quitt
    global tNodeStatus
    global aNodeStatus
    global rNodeStatus
    user = 0
    ends = 0
    while 0 in aNodeStatus or not endQueue.empty():
        user = 0
        while user == 0 and (0 in aNodeStatus or not endQueue.empty()):
            try:
                user = endQueue.get_nowait()
            except:
                time.sleep(1)
        try:
            putInQueue(user)
        except Exception as e:
            exceptions.put_nowait(e)
            #print("couldnt end " + str(user))
    while 0 in tNodeStatus or 0 in aNodeStatus or 0 in rNodeStatus:
        time.sleep(1)
    time.sleep(1)
    with open("save.json","w+") as json_file:
        json.dump(save, json_file,indent=4)
    quit(1)
    #putInQueue(user)
    #print("done")



try:
    with open("save.json") as json_file:
        save = json.load(json_file)
    with open("stats.json") as json_file:
        stats = json.load(json_file)
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    with open("backups/backup_"+dt_string+".json", "w+") as json_file:
        json.dump(save, json_file,indent=4)
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    with open("statsbackups/statsbackup_" + dt_string + ".json", "w+") as json_file:
        json.dump(stats, json_file, indent=4)
except Exception as e:
    exceptions.put_nowait(e)
    #print("Could Not Open File or Save Backup Aborting process")
    exit(1)

def initUser(user:int):
    u = str(user)
    save[u] = {}
    save[u]["timeline"] = []
    save[u]["interactions"] = {}
    #save[u]["interactions"]["init"] = 0
    save[u]["retweets"] = {}
    save[u]["retweets"]["init"] = 0
    save[u]["replies"] = []


def getTimeline(user:int):
    #print("got to Timeline")
    if str(user) not in save.keys():
        initUser(user)
    if len(save[str(user)]["timeline"]) == 0 or reloadTimelines:
        save[str(user)]["timeline"] = getInfo(user)
        replyQueue.put(user)
    #save[str(user)]["timeline"] = getInfo(user)
    #replyQueue.put(user)
    else:
        replyQueue.put(user)

def getInfo(user:int)->[]:
    global stats
    rett = api.user_timeline(user)
    #print("called Timeline " + str(user))
    person = api.get_user(user)
    followers = person.followers_count
    friends = person.friends_count
    favourites = person.favourites_count
    statuses = person.statuses_count
    ret = []
    for k in rett:
        ret.append(str(k.id))
        if str(k.id) not in stats.keys():
            stats[str(k.id)] = {}
            stats[str(k.id)]["followers"] = followers
            stats[str(k.id)]["friends"] = friends
            stats[str(k.id)]["favourited"] = favourites
            stats[str(k.id)]["statuscount"] = statuses
            j = abs(int((k.created_at - datetime.now()).total_seconds()))
            stats[str(k.id)]["time"] = j
            try:
                stats[str(k.id)]["favourites"] = k.retweeted_status.favorite_count
                stats[str(k.id)]["time"] = abs(int((k.retweeted_status.created_at - datetime.now()).total_seconds()))
            except:
                stats[str(k.id)]["favourites"] = k.favorite_count

            stats[str(k.id)]["retweets"] = k.retweet_count
    return ret


def getRetweets(ids:[], user:int):
    #print("got to Retweets")
    if save[str(user)]["retweets"]["init"] == 0 or reloadRetweets:
        for x in ids:
            k = api.retweeters(x)
            #print("called retweet")
            ret = []
            for i in k:
                ret.append(str(i))
            save[str(user)]["retweets"][str(x)] = ret
            replyQueue.put(user)
    else:
        replyQueue.put(user)

def getReplies(user:int):
    global browser
    #print("got to Replies")
    if len(save[str(user)]["replies"]) == 0 or reloadReplies:
        #path = os.path.abspath("geckodriver")
        #options = webdriver.FirefoxOptions()
        #options.add_argument('-headless')

        #browser = webdriver.Firefox(executable_path=path, firefox_options=options)

        i = 0
        for x in save[str(user)]["timeline"]:
            #if i == 5 :
                #break
            time.sleep(1)
            browser.get("https://twitter.com/i/web/status/" + x)
            soup = BeautifulSoup(browser.page_source, "lxml")
            data = soup.find_all(class_="account-group")
            datum = []
            for x in data:
                if x.has_attr("data-user-id"):
                    datum.append(x["data-user-id"])
            ret = datum
            save[str(user)]["replies"] += ret
            i+=1
    analyzeQueue.put(user)
def analyze(user:id):
    #print("got to Analyze")
    interactions = {}
    suser = str(user)
    for x in save[suser]["retweets"].keys():
        for i in x:
            if i not in interactions.keys() and len(i) != 1:
                interactions[i] = 1
            elif len(i) != 1:
                interactions[i] += 1
    for x in save[suser]["replies"]:
        if x not in interactions.keys() and len(x) != 1:
            interactions[x] = 1
        elif len(x) != 1:
            interactions[x] += 1
    for x in interactions.keys():
        save[suser]["interactions"][x] = interactions[x]
    endQueue.put(user)
def putInQueue(user:id):
    kil = list(map(int, save[str(user)]["interactions"].keys()))
    for x in kil:
        idQueue.put(x)

initThreads()

for x in range(0, timelineNodeA):
    timelineNodes[x].start()
for x in range(0, replyNodeA):
    replyNode[x].start()
for x in range(0, analyzeNodeA):
    analyzeNode[x].start()

backup = threading.Thread(target=backupThread,daemon=True,args=[0])
backup.start()
#endNode.start()
endNode = threading.Thread(target=endNodeJob, daemon=True, args=[0])

sel = 0
class Screen(object):
    UP = -1
    DOWN = 1

    def __init__(self, items):
        """ Initialize the screen window
        Attributes
            window: A full curses screen window
            width: The width of `window`
            height: The height of `window`
            max_lines: Maximum visible line count for `result_window`
            top: Available top line position for current page (used on scrolling)
            bottom: Available bottom line position for whole pages (as length of items)
            current: Current highlighted line number (as window cursor)
            page: Total page count which being changed corresponding to result of a query (starts from 0)
            ┌--------------------------------------┐
            |1. Item                               |
            |--------------------------------------| <- top = 1
            |2. Item                               |
            |3. Item                               |
            |4./Item///////////////////////////////| <- current = 3
            |5. Item                               |
            |6. Item                               |
            |7. Item                               |
            |8. Item                               | <- max_lines = 7
            |--------------------------------------|
            |9. Item                               |
            |10. Item                              | <- bottom = 10
            |                                      |
            |                                      | <- page = 1 (0 and 1)
            └--------------------------------------┘
        Returns
            None
        """
        self.window = None

        self.width = 0
        self.height = 0

        self.init_curses()

        self.items = items

        self.max_lines = curses.LINES
        self.top = 0
        self.bottom = len(self.items)
        self.current = 0
        self.page = self.bottom // self.max_lines

    def init_curses(self):
        """Setup the curses"""
        self.window = curses.initscr()
        self.window.keypad(True)

        curses.noecho()
        curses.cbreak()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)

        self.current = curses.color_pair(2)

        self.height, self.width = self.window.getmaxyx()

    def run(self):
        """Continue running the TUI until get interrupted"""
        try:
            input_stream(self)
        except KeyboardInterrupt:
            pass
        finally:
            curses.endwin()




    def scroll(self, direction)->bool:
        """Scrolling the window when pressing up/down arrow keys"""
        # next cursor position after scrolling
        next_line = self.current + direction

        # Up direction scroll overflow
        # current cursor position is 0, but top position is greater than 0
        if (direction == self.UP) and (self.top > 0 and self.current == 0):
            self.top += direction
            return True
        # Down direction scroll overflow
        # next cursor position touch the max lines, but absolute position of max lines could not touch the bottom
        if (direction == self.DOWN) and (next_line == self.max_lines) and (self.top + self.max_lines < self.bottom):
            self.top += direction
            return True
        # Scroll up
        # current cursor position or top position is greater than 0
        if (direction == self.UP) and (self.top > 0 or self.current > 0):
            self.current = next_line
            return True
        # Scroll down
        # next cursor position is above max lines, and absolute position of next cursor could not touch the bottom
        if (direction == self.DOWN) and (next_line < self.max_lines) and (self.top + next_line < self.bottom):
            self.current = next_line
            return True
        return False

    def paging(self, direction):
        """Paging the window when pressing left/right arrow keys"""
        current_page = (self.top + self.current) // self.max_lines
        next_page = current_page + direction
        # The last page may have fewer items than max lines,
        # so we should adjust the current cursor position as maximum item count on last page
        if next_page == self.page:
            self.current = min(self.current, self.bottom % self.max_lines - 1)

        # Page up
        # if current page is not a first page, page up is possible
        # top position can not be negative, so if top position is going to be negative, we should set it as 0
        if (direction == self.UP) and (current_page > 0):
            self.top = max(0, self.top - self.max_lines)
            return
        # Page down
        # if current page is not a last page, page down is possible
        if (direction == self.DOWN) and (current_page < self.page):
            self.top += self.max_lines
            return

    def display(self):
        """Display the items on window"""
        self.window.erase()
        for idx, item in enumerate(self.items[self.top:self.top + self.max_lines]):
            # Highlight the current cursor line
            if idx == self.current:
                self.window.addstr(idx, 0, item, curses.color_pair(2))
            else:
                self.window.addstr(idx, 0, item, curses.color_pair(1))
        self.window.refresh()

def input_stream(self):
    global sel
    """Waiting an input and run a proper method according to type of input"""
    while True:
        self.display()
        ch = self.window.getch()
        if ch == curses.KEY_UP:
            if(self.scroll(self.UP)):
                sel -= 1
        elif ch == curses.KEY_DOWN:
            if(self.scroll(self.DOWN)):
                sel += 1
        elif ch == curses.KEY_LEFT:
            self.paging(self.UP)
        elif ch == curses.KEY_RIGHT:
            self.paging(self.DOWN)
        elif ch == curses.KEY_ENTER:
            break
        elif ch == curses.ascii.ESC:
            break


def main():
    switchboard("nah")
    global browser
    browser.quit()

def switchboard(type:str):
    global sel
    notExit = True
    lines = ['status',"exceptions", "threads", "backup", "Close Program"]
    while(notExit):
        if(type == "backup"):
            lines = backupInfo
        elif(type == "threads"):
            lines = threadInfo()
        elif(type == "status"):
            lines = statusInfo()
        elif(type == "exceptions"):
            lines = ExceptionsInfo()
        elif(type == "backupnow"):
            lines = ["backingup up will hang the TUI, please be wait until the program stops hanging to proceed", "back"]
        elif(type == "backingup"):
            truth = backupThread(1)
            if(truth):
                lines = ["success", "back"]
            else:
                lines = ["unsuccessful", "exceptions" ,"back"]
        elif(type == "back"):
            lines = ['status',"exceptions", "threads", "backup", "Close Program"]
        elif(type == "Close"):
            lines = ["exiting the program will ensure unsaved data is lost, please backup before exiting","kill the program", "backupnow", "back"]
        elif(type == "kill"):
            lines = statusInfo()
            notExit = False
            continue
        screen = Screen(lines)
        screen.run()
        type = lines[sel].split(" ")[0]
        sel = 0
        # try:
        #     type = lines[sel].split(" ")[0]
        # except IndexError:
        #     type = "back"
        #     print(sel)

def backuptext() -> []:
    return backupInfo
def ExceptionsInfo()->[]:
    while exceptions.qsize() != 0:
        Net.append(exceptions.get_nowait())
    if len(Net) == 0:
        ret = ["no exceptions","back"]
        return ret
    ret = list(map(repr,Net))
    ret.append("back")
    return ret
def threadInfo()->[]:
    temp = [""]*(timelineNodeA+replyNodeA+analyzeNodeA)
    i = 0
    for s in tNodeStatus:
        temp[i] = "thread"+str(i)+" timelineThread " + str(s)
        i+=1
    for s in rNodeStatus:
        temp[i] = "thread" + str(i) + " replyThread " + str(s)
        i+=1
    for s in aNodeStatus:
        temp[i] = "thread" + str(i) + " analyzeThread " + str(s)
        i+=1
    temp.append("back")
    return temp
def statusInfo()->[]:
    temp = ["succesfully analyzed 56", "preliminary on 100", "statuses remaining","retweets remaining","shows remaining","user_timelines remaining","lookups remaining" "uptime", "back"]
    temp[0] = "succesfully analyzed " + str(len(save))
    temp[1] = "preliminary on " + str(len(stats))
    t=api.rate_limit_status()
    s = t['resources']['lists']['/lists/statuses']['remaining']
    s1 = t['resources']['users']['/users/show/:id']['remaining']
    s2 = t['resources']['statuses']['/statuses/user_timeline']['remaining']
    s3 = t['resources']['statuses']['/statuses/retweets/:id']['remaining']
    s4 = t['resources']['statuses']['/statuses/lookup']['remaining']
    temp[2] = "statuses remaining " + str(s)
    temp[3] = "retweets remaining " + str(s3)
    temp[4] = "shows remaining " + str(s1)
    temp[5] = "user_timelines remaining " + str(s2)
    temp[6] = "lookups remaining " + str(s4)
    temp[7] = "uptime " + str(time.time()-start_time)
    temp.append("back")
    return temp




start_time = time.time()
if __name__ == '__main__':
    main()
