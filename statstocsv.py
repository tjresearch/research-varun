import json
import csv

stats = {}

with open("stats.json") as json_file:
    stats = json.load(json_file)

with open("csvfile.csv", "w+") as csv_file:
    we = csv.writer(csv_file, delimiter = ',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    we.writerow(["followers","friends","favourited","statuscount","favourites","retweets","time"])
    for k in stats.keys():
        followers = int(stats[str(k)]["followers"])
        friends = int(stats[str(k)]["friends"])
        favourites = int(stats[str(k)]["favourited"])
        statuses = int(stats[str(k)]["statuscount"])
        favorites = int(stats[str(k)]["favourites"])
        retweets = int(stats[str(k)]["retweets"])
        time = int(stats[str(k)]["time"])
        we.writerow([followers,friends,favourites,statuses,favorites,retweets,time])
