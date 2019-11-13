import json
from datetime import datetime

cleanInter = True
cleanReply = True
cleanTimeline = True
cleanRetweet = True
cleanUser = True

save = {}

try:
    with open("save.json") as json_file:
        save = json.load(json_file)
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    with open("backup_"+dt_string+".json", "w+") as json_file:
        json.dump(save, json_file,indent=4)
except:
    print("Could Not Open File or Save Backup Aborting process")
    exit(1)
if not cleanUser:
    for x in save.keys():
        if cleanInter:
            save[x]["interactions"] = {}
        if cleanReply:
            save[x]["replystatus"] = []
        if cleanTimeline:
            save[x]["timeline"] = []
        if cleanRetweet:
            save[x]["posts"] = {}
if cleanUser:
    save = {}
with open("save.json", "w+") as json_file:
    json.dump(save,json_file,indent=4)
