import tweepy
import queue
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os

path = os.path.abspath("geckodriver")
options = webdriver.FirefoxOptions()
options.add_argument('-headless')

browser = webdriver.Firefox(executable_path=path, firefox_options=options)

useSavedData = False

api = tweepy.API()

testing = 0
save = {}

def init():
  global api
  global save
  consumer_key = "iTgGukoBAPecLL5awvC0b7jp7"
  consumer_secret = "2jXCBmYLBSubcXtCljbSP1eBfsUbeFgUlsclswt8tQ5Gn4DDXf"
  access_token = "1166697426318757888-QBNkGhVY8bqeycxRulTLYAiZrhnN1m"
  access_token_secret = "d0zLEPH8ZqNSePfyaZqIpCEHp7CfdJh04u7V3lscRh2ev"
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth)
  with open("save.json") as json_file:
    save = json.load(json_file)
init()



q = queue.Queue()

Us  = {} #dict[int:dict[int:int]]

depth = 3

# consumer_key = "iTgGukoBAPecLL5awvC0b7jp7"
# consumer_secret = "2jXCBmYLBSubcXtCljbSP1eBfsUbeFgUlsclswt8tQ5Gn4DDXf"
# access_token = "1166697426318757888-QBNkGhVY8bqeycxRulTLYAiZrhnN1m"
# access_token_secret = "d0zLEPH8ZqNSePfyaZqIpCEHp7CfdJh04u7V3lscRh2ev"
# auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)
#
# api = tweepy.API(auth)

u1 = api.get_user("@FoxNews")

def initUser(iid: int):
  save[str(iid)] = {}
  save[str(iid)]["retweets"] = {}
  save[str(iid)]["interactions"] = {}
  #save[str(iid)]["timeline"] = []
  save[str(iid)]["replies"] = []






def getUserTimeline(iid: int) -> []:
  if str(iid) not in save.keys():
    initUser(iid)
  if str(iid) in save.keys() and "timeline" in save[str(iid)].keys():
    return list(map(int, save[str(iid)]["timeline"]))
  rett = api.user_timeline(iid)
  ret = []
  for k in rett:
    ret.append(str(k.id))
  if str(iid) in save.keys():
    save[str(iid)]["timeline"] = ret
  else:
    save[str(iid)] = {}
    save[str(iid)]["timeline"] = ret


  return ret
def getRetweets(time:int, idd:int):
  if str(time) in save[str(idd)]["retweets"].keys():
    return list(map(int, save[str(idd)]["retweets"][str(time)]))
  k = api.retweeters(time)
  ret = []
  for i in k:
    ret.append(str(i))
  save[str(idd)]["retweets"][str(time)] = ret
def getReplyStasus(status:str, iid:int):
  #if str(status) in save[str(iid)]["replystasus"]:
  #  return list(map(int, save[str(iid)]["replystasus"]))
  if not useSavedData:
    browser.get("https://twitter.com/i/web/status/"+status)
    time.sleep(1)
    soup = BeautifulSoup(browser.page_source)
    data = soup.find_all(class_= "account-group")
    datum = []
    for x in data:
      if x.has_attr("data-user-id"):
        datum.append(x["data-user-id"])
    ret = datum
    save[str(iid)]["replies"] += ret
    return ret
def analyze(user):
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


init()

q.put(u1.id)

i = 1
# try:
#   while q.qsize() != 0 and i <= depth:
#     user = q.get()
#     Us[user] = {}
#     mentions = getUserTimeline(user)
#     for m in mentions:
#        b = getRetweets(m, user)
#        getReplyStasus(str(m), user)
#     analyze(user)
#     print(Us)
#   with open("save.json", "w+") as json_file:
#     json.dump(save,json_file,indent=4)
#   browser.quit()
# except Exception as e:
#   print(e)
#   with open("save.json", "w+") as json_file:
#     json.dump(save,json_file,indent=4)
#   browser.quit()

while q.qsize() != 0 and i <= depth:
  user = q.get()
  Us[user] = {}
  mentions = getUserTimeline(user)
  for m in mentions:
     b = getRetweets(m, user)
     getReplyStasus(str(m), user)
  analyze(user)
  print(Us)
with open("save.json", "w+") as json_file:
  json.dump(save,json_file,indent=4)
browser.quit()






