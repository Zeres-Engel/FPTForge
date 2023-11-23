import json
f = open("app\emb1.json")
p = open("app\people.json")
data = json.load(f)
people = json.load(p)
res = {}
for people_id, emb in data.items():
    if people_id in people:
        res[people_id] = [emb]

print('before', len(data.keys()))
with open("app\emb1.json", "w") as outfile: 
    json.dump(res, outfile)
print('after', len(res.keys()))