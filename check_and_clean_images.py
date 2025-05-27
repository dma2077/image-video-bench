import json
import os
from pathlib import Path

# 定义路径
jsonl_file = "all_data_v3.jsonl"
image_dir = "/Users/dehua/code/image-video-bench/videos/images_0414"

# 从jsonl文件中读取所有图像名称
jsonl_images = set()
with open(jsonl_file, 'r') as f:
    for line in f:
        data = json.loads(line)
        for video_id, annotations in data.items():
            for annotation in annotations:
                if 'image_name' in annotation:
                    jsonl_images.add(annotation['image_name'])

# 获取目录中的所有图像文件
dir_images = set()
for file in os.listdir(image_dir):
    if file.endswith(('.png', '.jpg', '.jpeg')):
        dir_images.add(file)

# 找出需要删除的文件（目录中有但jsonl中没有的）
files_to_delete = dir_images - jsonl_images

# 找出缺失的文件（jsonl中有但目录中没有的）
missing_files = jsonl_images - dir_images

# 打印结果
print(f"Total images in JSONL: {len(jsonl_images)}")
print(f"Total images in directory: {len(dir_images)}")
print(f"\nFiles to delete ({len(files_to_delete)}):")
for file in sorted(files_to_delete):
    print(f"- {file}")

print(f"\nMissing files ({len(missing_files)}):")
for file in sorted(missing_files):
    print(f"- {file}")

# 删除不需要的文件
for file in files_to_delete:
    file_path = os.path.join(image_dir, file)
    try:
        os.remove(file_path)
        print(f"Deleted: {file}")
    except Exception as e:
        print(f"Error deleting {file}: {e}") 