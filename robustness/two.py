import json


with open('outputs/' + 'data.json' , 'r', encoding='utf-8') as fp:
    source_data=json.load(fp)

with open('filename.json' , 'r', encoding='utf-8') as f:
    target=json.load(f)


    
# change what kind of data to take    
for item in source_data["drop_phrases"]:
    id_num = int(item["id"][:-1])# Extracting the first digit from the id
    bb_num = int(item["id"][-1])
    target["data"][id_num]["sents"][bb_num] = item["perturbed"]

# for key, value in temp_dict.items():
#     target_data["data"].append(value)

print(target)

with open('outputs/' + 'drop_phrases.json' , 'w') as a:
    json.dump(target,a)