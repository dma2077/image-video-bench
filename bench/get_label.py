import json

with open("/Users/dehua/code/image-video-bench/result.json", 'r', encoding='utf-8') as file:
    datas = json.load(file)

count = 0
neg_count = 0
for k , v in datas.items():
    if v == "是":
        count += 1
    elif v == "否":
        neg_count += 1

print(count)
print(neg_count)
