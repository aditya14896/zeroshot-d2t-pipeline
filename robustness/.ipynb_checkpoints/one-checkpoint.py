import json
source_data = []
with open("outputs/example-all.jsonl", 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        source_data.append(data)

print(source_data)
target_data = {}
for item in source_data:
    if item["type"] not in target_data:
        target_data[item["type"]] = []
    target_data[item["type"]].append({"id": item["id"], "perturbed": item["perturbed"]})

with open('outputs/' + 'data.json' , 'w') as fp:
    json.dump(target_data,fp)
        # for i in target_data:
        #     # i = i.encode('utf-8').decode('utf-8')
        #     json.dump(i, fp)
        #     fp.write("\n")
    fp.close()