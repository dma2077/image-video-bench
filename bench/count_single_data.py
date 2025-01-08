import os
import json

valid_count = 0
file_path = "/Users/dehua/code/image-video-bench/res/res_current/ans_dehua4.jsonl"
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file.readlines():
        line = json.loads(line)
        for k, v in line.items():
            for data in v:
                if data["image_name"] != '':
                    valid_count += 1

print(valid_count)
            
