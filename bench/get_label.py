# import json

# with open("/Users/dehua/code/image-video-bench/result.json", 'r', encoding='utf-8') as file:
#     datas = json.load(file)

# count = 0
# neg_count = 0
# for k , v in datas.items():
#     if v == "是":
#         count += 1
#     elif v == "否":
#         neg_count += 1

# print(count)
# print(neg_count)

# import os

# def merge_ans_jsonl_files(input_dir, output_file):
#     """
#     Merge all .jsonl files starting with 'ans' in the specified directory into a single .jsonl file.

#     Args:
#         input_dir (str): Path to the directory containing .jsonl files.
#         output_file (str): Path to the output .jsonl file.
#     """
#     with open(output_file, 'w', encoding='utf-8') as outfile:
#         for filename in os.listdir(input_dir):
#             if filename.startswith("ans") and filename.endswith(".jsonl"):  # 筛选以 'ans' 开头的 .jsonl 文件
#                 file_path = os.path.join(input_dir, filename)
#                 print(f"Processing file: {file_path}")
#                 with open(file_path, 'r', encoding='utf-8') as infile:
#                     for line in infile:
#                         outfile.write(line)  # 将每行写入输出文件

#     print(f"All 'ans' JSONL files merged into {output_file}")

# # 指定输入目录和输出文件路径
# input_directory = "./res/res_current"
# output_jsonl_file = "./res/res_current/questions.jsonl"

# # 执行合并
# merge_ans_jsonl_files(input_directory, output_jsonl_file)






import os
import shutil

def copy_images_to_target_dir(base_dir, target_dir_name="images"):
    """
    Copy all images from subdirectories (excluding the target directory) into the target directory.

    Args:
        base_dir (str): The base directory containing subdirectories with images.
        target_dir_name (str): The name of the target directory to copy images into.
    """
    # 确保目标目录存在
    target_dir = os.path.join(base_dir, target_dir_name)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created target directory: {target_dir}")

    # 遍历子目录
    for subdir in os.listdir(base_dir):
        subdir_path = os.path.join(base_dir, subdir)
        if os.path.isdir(subdir_path) and subdir != target_dir_name:  # 排除目标目录
            print(f"Processing directory: {subdir_path}")
            for filename in os.listdir(subdir_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # 筛选图片文件
                    source_path = os.path.join(subdir_path, filename)
                    target_path = os.path.join(target_dir, filename)

                    # 如果目标文件已存在，重命名文件
                    if os.path.exists(target_path):
                        continue

                    # 复制文件
                    shutil.copy2(source_path, target_path)
                    print(f"Copied {source_path} to {target_path}")

    print(f"All images have been copied into {target_dir}")

# 指定基础目录
base_directory = "./videos/upload_images"

# 执行复制
copy_images_to_target_dir(base_directory)




import os

def count_images_in_directory(base_dir):
    """
    Count the number of image files in the specified directory and its subdirectories.

    Args:
        base_dir (str): The base directory to search for images.

    Returns:
        int: Total number of image files.
    """
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')  # 支持的图片扩展名
    image_count = 0

    for root, _, files in os.walk(base_dir):  # 遍历目录及其子目录
        for file in files:
            if file.lower().endswith(image_extensions):  # 判断是否是图片
                image_count += 1

    return image_count

# 指定基础目录
base_directory = "./videos/upload_images/images"

# 统计图片数量
total_images = count_images_in_directory(base_directory)

# 输出结果
print(f"Total number of images in '{base_directory}': {total_images}")