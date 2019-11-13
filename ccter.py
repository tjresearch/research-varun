import tweepy
import bs4
import lxml
import json


api = tweepy.API()

testing = 0
save = {}




def init():
    global api
    global data
    consumer_key = "iTgGukoBAPecLL5awvC0b7jp7"
    consumer_secret = "2jXCBmYLBSubcXtCljbSP1eBfsUbeFgUlsclswt8tQ5Gn4DDXf"
    access_token = "1166697426318757888-QBNkGhVY8bqeycxRulTLYAiZrhnN1m"
    access_token_secret = "d0zLEPH8ZqNSePfyaZqIpCEHp7CfdJh04u7V3lscRh2ev"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    with open("save.json") as json_file:
        data = json.load(json_file)

def getUserTimeline(iid:int) -> []:
    if str(iid) in save.keys and "timeline" in save[str(iid)].keys():
        return map(int, save[str(iid)]["timeline"])
    return api.user_timeline(iid)
