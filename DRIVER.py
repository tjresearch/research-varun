import tweepy
from multiprocessing import Queue
import json
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
import threading


reloadTimelines = False
reloadInteractions = False
reloadRetweets = False
reloadReplies = False
useSavedData = False

quitt = False

idQueue = Queue()
replyQueue = Queue()
analyzeQueue = Queue()
endQueue = Queue()
endNode:threading.Thread
save = {}
api = tweepy.API()
stats = {}

timelineNodeA = 2
replyNodeA = 1
analyzeNodeA = 2

timelineNodes = []
replyNode = []
analyzeNode = []

tNodeStatus = [0] * timelineNodeA
rNodeStatus = [0] * replyNodeA
aNodeStatus = [0] * analyzeNodeA


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
  api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
init()

u1 = api.get_user(612473)
idQueue.put(u1.id)
#u2 = api.get_user("FoxNews")
#idQueue.put(u2.id)

def backupThread(x:int):
    while True:
        try:
            with open("save.json") as json_file:
                now = datetime.now()
                dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
                with open("backups/backup_" + dt_string + ".json", "w+") as json_file:
                    json.dump(save, json_file, indent=4)
        except:
            now = datetime.now()
            print("Warning couldnt backup " + now.strftime("%d_%m_%Y_%H_%M_%S"))

        try:
            now = datetime.now()
            dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
            with open("statsbackups/statsbackup_" + dt_string + ".json", "w+") as json_file:
                json.dump(stats, json_file, indent=4)
        except:
            now = datetime.now()
            print("Warning couldnt statsbackup " + now.strftime("%d_%m_%Y_%H_%M_%S"))

        if x != 0:
            break
        time.sleep(60)


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
            print("got to Timeline " + str(user))
            try:
                getTimeline(user)
            except:
                print("couldnt get Timeline " + str(user))
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
            except:
                print("couldnt get info " + str(user))
    tNodeStatus[x] = 1
    backupThread(30)
    print("done with t " + str(x))

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
        print("got to replies " + str(user))
        try:
            getReplies(user)
        except:
            print("couldnt get replies " + str(user))
    rNodeStatus[x] = 1
    print("done with r "+str(x))

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
        print("got to analyze " + str(user))
        try:
            analyze(user)
        except:
            print("could not analyze " + str(user))
    aNodeStatus[x] = 1
    print("done with A " + str(x))

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
        except:
            print("couldnt end " + str(user))
    while 0 in tNodeStatus or 0 in aNodeStatus or 0 in rNodeStatus:
        time.sleep(1)
    time.sleep(1)
    with open("save.json","w+") as json_file:
        json.dump(save, json_file,indent=4)
    quit(1)
    #putInQueue(user)
    print("done")



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
except:
    print("Could Not Open File or Save Backup Aborting process")
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
    print("called Timeline " + str(user))
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
            print("called retweet")
            ret = []
            for i in k:
                ret.append(str(i))
            save[str(user)]["retweets"][str(x)] = ret
            replyQueue.put(user)
    else:
        replyQueue.put(user)

def getReplies(user:int):
    #print("got to Replies")
    if len(save[str(user)]["replies"]) == 0 or reloadReplies:
        path = os.path.abspath("geckodriver")
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')

        browser = webdriver.Firefox(executable_path=path, firefox_options=options)
        i = 0
        for x in save[str(user)]["timeline"]:
            #if i == 5 :
                #break
            time.sleep(1)
            browser.get("https://twitter.com/i/web/status/" + x)
            soup = BeautifulSoup(browser.page_source)
            data = soup.find_all(class_="account-group")
            datum = []
            for x in data:
                if x.has_attr("data-user-id"):
                    datum.append(x["data-user-id"])
            ret = datum
            save[str(user)]["replies"] += ret
            i+=1
        browser.quit()
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
endNodeJob()
