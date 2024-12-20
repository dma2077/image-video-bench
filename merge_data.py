import json
import csv

json_path = './text_files/sampled_videos_ids_1100.json'
csv_path = './representative_video_ids_1100.csv'
new_json_path = './text_files/updated_sampled_videos_ids_1100.json'  # 新文件路径

# Step 1: 读取 JSON 文件
with open(json_path, 'r', encoding='utf-8') as file:
    old_json = json.load(file)

# Step 2: 读取 CSV 文件
replace_data = []
with open(csv_path, 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        replace_data.append(row[0])  # 假设每行只有一个元素

# Step 3: 构建新数据，按位置插入
new_sampled_ids = []  # 新的数据列表

replace_idx = 0  # 用于跟踪替换数据的位置

for i in range(len(old_json["sampled_id"])):
    # 如果是需要保留的索引范围，直接添加到新列表
    if i < 44 or (700 <= i < 730) or (1050 <= i < 1071) or (300 <= i < 340):
        new_sampled_ids.append(old_json["sampled_id"][i])
    else:
        # 否则，从 CSV 中取数据进行替换
        if replace_idx < len(replace_data):  # 防止越界
            new_sampled_ids.append(replace_data[replace_idx])
            replace_idx += 1
        else:
            new_sampled_ids.append(None)  # 如果 CSV 数据不够填充，插入 None

# Step 4: 更新 JSON 数据
new_json = {
    "sampled_id": new_sampled_ids
}

# Step 5: 将更新后的数据写入新 JSON 文件
with open(new_json_path, 'w', encoding='utf-8') as file:
    json.dump(new_json, file, ensure_ascii=False, indent=4)

print(f"数据已更新并保存到新文件：{new_json_path}")
