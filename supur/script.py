import json

names = []
with open("factionKey.json", "r") as f:
    for line in f:
        names.append(line.strip())

keyDict={}
for name in names:
    keyDict[name]=[]
    keyDict[name].append(name)

with open("factKey.json", "w+") as f:
    f.write(json.dumps(keyDict, indent=4))


