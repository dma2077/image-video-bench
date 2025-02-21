import os

def delete_matching_files(video_dir, converted_video_dir):
    # 获取两个目录下的文件名（去掉扩展名）
    video_files = {os.path.splitext(f)[0] for f in os.listdir(video_dir) if os.path.isfile(os.path.join(video_dir, f))}
    converted_files = {os.path.splitext(f)[0] for f in os.listdir(converted_video_dir) if os.path.isfile(os.path.join(converted_video_dir, f))}
    
    # 找出两个目录中都存在的文件（去掉扩展名）
    files_to_delete = video_files.intersection(converted_files)
    
    # 删除 videos 目录中对应的文件
    for file_name in files_to_delete:
        file_path = os.path.join(video_dir, file_name + ".mp4")  # 假设文件是 MP4 格式
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        else:
            print(f"File not found: {file_path}")

# 设置目录路径
video_dir = '/Users/dehua/code/image-video-bench/youtube_downloads/videos'
converted_video_dir = '/Users/dehua/code/image-video-bench/youtube_downloads/videos_converted'

# 执行删除操作
delete_matching_files(video_dir, converted_video_dir)