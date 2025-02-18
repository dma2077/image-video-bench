import os
import json

# 根目录路径
jsonl_directory = '/Users/dehua/code/image-video-bench/res/2_12'
image_directory_base = '/Users/dehua/code/image-video-bench/videos/upload_images'

# 存储缺失文件的记录
missing_files = set()

# 获取jsonl目录下的所有jsonl文件
jsonl_files = [f for f in os.listdir(jsonl_directory) if f.endswith('.jsonl')]

# 遍历所有jsonl文件
for jsonl_file in jsonl_files:
    # 提取文件名中的用户名部分
    username = jsonl_file.split('_')[1].split('.')[0]  # 假设文件命名格式为 ans_dehua1.jsonl
    
    # 对应的图片目录路径
    image_directory = os.path.join(image_directory_base, username)
    
    # 读取jsonl文件内容
    with open(os.path.join(jsonl_directory, jsonl_file), 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 遍历每一行
    for line in lines:
        data = json.loads(line.strip())
        
        # 遍历所有的键
        for key, value in data.items():
            # 如果键对应的值是一个列表
            if isinstance(value, list):
                # 遍历列表中的每个字典
                for item in value:
                    image_name = item.get('image_name')
                    
                    if image_name:
                        # 检查文件是否存在于图片目录中
                        image_path = os.path.join(image_directory, image_name)
                        if not os.path.exists(image_path):
                            missing_files.add((jsonl_file, key, image_name))  # 记录缺失的文件、键名和文件名

# 输出缺失文件的信息以及个数
if missing_files:
    print("以下文件不存在于目标图片目录中:")
    for jsonl_file, key, image_name in missing_files:
        print(f"JSONL文件: {jsonl_file}, 键: {key}, 文件: {image_name}")
    
    print(f"\n总共有 {len(missing_files)} 个文件不存在于目标图片目录中")
else:
    print("所有文件都存在于目标图片目录中")