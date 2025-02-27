import os

def count_files(directory):
    """
    统计指定目录及其子目录中的所有文件数量。

    参数:
    directory (str): 要统计的目录路径。

    返回:
    int: 文件总数。
    """
    total_files = 0
    for root, dirs, files in os.walk(directory):
        total_files += len(files)
    return total_files

if __name__ == "__main__":
    directory = "/Users/dehua/code/image-video-bench/videos/upload_images"
    
    if os.path.exists(directory) and os.path.isdir(directory):
        total = count_files(directory)
        print(f"目录 '{directory}' 中的文件总数: {total}")
    else:
        print(f"目录 '{directory}' 不存在或不是一个有效的目录。")