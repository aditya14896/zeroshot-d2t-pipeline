import json

# Open the JSON file
with open('original_format.json') as f:
    source_data = json.load(f)

target_data = []
    
for i, data in enumerate(source_data["data"]):
    for j,sents in enumerate(data["sents"]):
        target_data.append({"id": str(i)+str(j), "references": sents})


print(target_data)

with open('output.jsonl', 'w') as file:
    # Loop through the data and write each item to a new line in the file
    for item in target_data:
        file.write(str(item) + '\n')