import json
import csv
import os

json_path = './text_files/updated_sampled_videos_ids_1100.json'
csv_path = './representative_video_ids_1000.csv'
new_json_path = './text_files/updated_sampled_videos_ids_1226.json'  # 新文件路径


# 定义路径
directory_path = '/Users/dehua/code/image-video-bench/res/res_current'
annotations_datas = []

# 获取目录下所有的jsonl文件
for filename in os.listdir(directory_path):
    if filename.endswith('.jsonl'):  # 只处理jsonl文件
        file_path = os.path.join(directory_path, filename)
        
        # 读取每个jsonl文件的内容
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                data = json.loads(line)
                # 将数据添加到annotations_datas中
                annotations_datas.append(list(data.keys())[0])

print(annotations_datas)

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
    if i < 200 or (700 <= i < 730) or (1050 <= i < 1081) or (300 <= i < 370) or old_json["sampled_id"][i] in annotations_datas:
        new_sampled_ids.append(old_json["sampled_id"][i])
    else:
        # 否则，从 CSV 中取数据进行替换
        if replace_idx < len(replace_data):  # 防止越界
            new_sampled_ids.append(replace_data[replace_idx])
            replace_idx += 1
        else:
            new_sampled_ids.append(old_json["sampled_id"][i])  # 如果 CSV 数据不够填充，插入 None

# Step 4: 更新 JSON 数据
new_json = {
    "sampled_id": new_sampled_ids
}

# Step 5: 将更新后的数据写入新 JSON 文件
with open(new_json_path, 'w', encoding='utf-8') as file:
    json.dump(new_json, file, ensure_ascii=False, indent=4)

print(f"数据已更新并保存到新文件：{new_json_path}")




import json
import csv
import os

# Paths to your JSON and CSV files
json_path = './text_files/updated_sampled_videos_ids_1100.json'
csv_path = './representative_video_ids_1000.csv'
new_json_path = './text_files/updated_sampled_videos_ids_1226.json'  # New file path

# Directory containing JSONL files
directory_path = '/Users/dehua/code/image-video-bench/res/res_current'

# Initialize list to hold annotations data
annotations_datas = []

# Initialize a dictionary to map IDs to their source JSONL files
id_to_files_map = {}

# Get all JSONL files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith('.jsonl'):  # Only process JSONL files
        file_path = os.path.join(directory_path, filename)
        
        # Read each JSONL file
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    data = json.loads(line)
                    # Extract the ID (assuming the first key is the ID)
                    id_ = list(data.keys())[0]
                    annotations_datas.append(id_)
                    
                    # Update the mapping from ID to file
                    if id_ in id_to_files_map:
                        id_to_files_map[id_].add(filename)
                    else:
                        id_to_files_map[id_] = {filename}
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in file {filename}: {e}")
                except IndexError:
                    print(f"Empty JSON object in file {filename}: {line}")

print(f"Total IDs collected: {len(annotations_datas)}")

# # Paths to the two JSON files to compare
# a_json_path = '/Users/dehua/code/image-video-bench/text_files/updated_sampled_videos_ids_1100.json'
# b_json_path = '/Users/dehua/code/image-video-bench/text_files/updated_sampled_videos_ids_1226.json'

# def load_sampled_ids(json_path):
#     """
#     Load sampled_id list from a JSON file.

#     Args:
#         json_path (str): Path to the JSON file.

#     Returns:
#         list: List of sampled IDs.
#     """
#     try:
#         with open(json_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             sampled_ids = data.get('sampled_id', [])
#             if not isinstance(sampled_ids, list):
#                 raise ValueError(f"'sampled_id' in {json_path} is not a list.")
#             return sampled_ids
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON from {json_path}: {e}")
#         return []
#     except FileNotFoundError:
#         print(f"File not found: {json_path}")
#         return []
#     except Exception as e:
#         print(f"An error occurred while loading {json_path}: {e}")
#         return []

# # Load sampled_id lists from both JSON files
# a_sampled_ids = load_sampled_ids(a_json_path)
# b_sampled_ids = load_sampled_ids(b_json_path)

# # Create dictionaries for faster lookup (ID -> index)
# a_id_to_index = {id_: idx for idx, id_ in enumerate(a_sampled_ids)}
# b_id_to_index = {id_: idx for idx, id_ in enumerate(b_sampled_ids)}

# # Initialize list to hold discrepancies
# discrepancies = []

# # Iterate over each ID in annotations_datas and compare indices
# for id_ in annotations_datas:
#     a_index = a_id_to_index.get(id_)
#     b_index = b_id_to_index.get(id_)
    
#     if a_index is None:
#         print(f"ID '{id_}' not found in {a_json_path}.")
#         discrepancies.append({
#             'id': id_,
#             'a_index': 'Not Found',
#             'b_index': b_index if b_index is not None else 'Not Found',
#             'files': ', '.join(id_to_files_map.get(id_, [])) if id_ in id_to_files_map else 'None'
#         })
#         continue
    
#     if b_index is None:
#         print(f"ID '{id_}' not found in {b_json_path}.")
#         discrepancies.append({
#             'id': id_,
#             'a_index': a_index,
#             'b_index': 'Not Found',
#             'files': ', '.join(id_to_files_map.get(id_, [])) if id_ in id_to_files_map else 'None'
#         })
#         continue
    
#     if a_index != b_index:
#         discrepancies.append({
#             'id': id_,
#             'a_index': a_index,
#             'b_index': b_index,
#             'files': ', '.join(id_to_files_map.get(id_, [])) if id_ in id_to_files_map else 'None'
#         })

# # Report the results
# if not discrepancies:
#     print("✅ All elements in 'annotations_datas' have the same positions in both JSON files.")
# else:
#     print(f"❌ Found {len(discrepancies)} discrepancies between the JSON files:")
#     for d in discrepancies:
#         print(f" - ID '{d['id']}': a.jsonl index = {d['a_index']}, b.jsonl index = {d['b_index']}, Files = {d['files']}")
    