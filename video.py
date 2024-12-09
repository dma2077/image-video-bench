import os
import json
from moviepy.editor import VideoFileClip

def get_mp4_files(current_dir, min_duration):
    
    # 列出当前目录下的所有文件和文件夹
    all_files = os.listdir(current_dir)
    
    # 筛选出以 .mp4 结尾的文件
    mp4_files = [file.replace(".mp4", '') for file in all_files if file.lower().endswith('.mp4')]
    
    for video in mp4_files:
        video_path = current_dir + "/" + video + ".mp4"
        video = VideoFileClip(video_path)
        print(vide.duration)
        if video.duration < min_duration:
            mp4_files.pop(video)
    return mp4_files

# 示例使用
if __name__ == "__main__":
    mp4_list = get_mp4_files('/map-vepfs/dehua/data/image-video-bench/image-video-bench/videos/examples/youtube_0518', "100")
    print("当前目录下的MP4文件列表：")
    with open('./text_files/sampled_id_youtube_0518.json', 'w') as file:
        sample = {}
        sample["sampled_id"] = mp4_list
        json.dump(sample, file, indent=4)
    
