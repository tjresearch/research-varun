import json
import csv
from operator import itemgetter
stats = {}
logs = []
a = .27223896
b = 2.09931222
with open("stats.json") as stat:
    stats = json.load(stat)
for k in stats.keys():
    x = int(stats[str(k)]["favourites"])
    y = int(stats[str(k)]["retweets"])
    dist1 = (x+(y*a))/(1+pow(a,2))
    dist2 = (x+(y*b))/(1+pow(b,2))
    mindist = dist1
    # if dist1 < dist2:
    #     mindist = dist1
    logs.append((int(k), mindist))
#print(logs)
ka = sorted(logs, key=itemgetter(1))
ka.reverse()

with open("weirdness.txt", "w+") as out:
    for x in ka:
        out.write(str(x)+"\n")
with open("csvweird.csv", "w+") as csv_file:
    we = csv.writer(csv_file, delimiter = ',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    #we.writerow(["followers","friends","favourited","statuscount","favourites","retweets","time"])
    for k in ka:
        favorites = int(stats[str(k[0])]["favourites"])
        retweets = int(stats[str(k[0])]["retweets"])
        if favorites > 100 and retweets > 100:

            weirdness = k[1]
            #time = int(stats[str(k)]["time"])
            we.writerow([favorites,retweets,weirdness])
