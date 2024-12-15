import yt_dlp
import os
import json

# 创建下载文件夹
def create_download_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# 下载视频
def download_youtube_video(video_id, download_folder):
    video_folder = os.path.join(download_folder, 'videos')
    create_download_folder(video_folder)
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]',  # 下载最佳 MP4 格式视频
        'outtmpl': os.path.join(video_folder, '%(id)s.%(ext)s'),  # 设置保存文件名
        'quiet': False,  # 输出详细信息
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=True)
        return {
            "cate": result.get('cate', None),
            "query": result.get('query', None),
            "url": result.get('webpage_url', None),
            "video_id": video_id,
            "title": result.get('title', 'Unknown title'),
            "description": result.get('description', ''),
            "quality": result.get('format_note', 'Unknown quality'),
            "duration": result.get('duration', 0),
            "publish_time": result.get('upload_date', 'Unknown date'),
        }

# 下载音频
def download_youtube_audio(video_id, download_folder):
    audio_folder = os.path.join(download_folder, 'audios')
    create_download_folder(audio_folder)
    
    ydl_opts = {
        'format': 'bestaudio/best',  # 下载最佳音频
        'outtmpl': os.path.join(audio_folder, '%(id)s.%(ext)s'),  # 设置保存文件名
        'quiet': False,  # 输出详细信息
        'postprocessors': [{  # 转换音频为 MP3 格式
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=True)

# 保存元数据到 JSONL 文件
def save_metadata(metadata, metadata_file):
    with open(metadata_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(metadata, ensure_ascii=False) + '\n')

# if __name__ == "__main__":
#     video_ids = []
#     with open('/map-vepfs/dehua/data/image-video-bench/image-video-bench/sample_video_ids_1222.txt', 'r', encoding='utf-8') as file:
#         for line in file.readlines():
#             video_ids.append(line.strip())
#     download_folder = "youtube_downloads"
#     metadata_file = "metadata.jsonl"
#     create_download_folder(download_folder)

#     for video_id in video_ids:
#         video_metadata = download_youtube_video(video_id, download_folder)

#         # 保存单一元数据格式
#         metadata = {
#             "cate": video_metadata.get('cate'),
#             "query": video_metadata.get('query'),
#             "url": video_metadata.get('url'),
#             "video_id": video_metadata.get('video_id'),
#             "title": video_metadata.get('title'),
#             "description": video_metadata.get('description'),
#             "quality": video_metadata.get('quality'),
#             "duration": video_metadata.get('duration'),
#             "publish_time": video_metadata.get('publish_time')
#         }
#         save_metadata(metadata, metadata_file)

#         download_youtube_audio(video_id, download_folder)

#         print(f"Downloaded video and audio for: {video_metadata['title']}")



from moviepy.editor import VideoFileClip, AudioFileClip
import os

# # 文件路径
# audio_folder = r"E:\Code\image-video-bench\youtube_downloads\audios"  # 音频文件夹路径
# video_folder = r"E:\Code\image-video-bench\youtube_downloads\videos"  # 视频文件夹路径
# output_folder = r"E:\Code\image-video-bench\youtube_downloads\outputs"  # 输出文件夹路径

# # 确保输出文件夹存在
# os.makedirs(output_folder, exist_ok=True)

# # 遍历视频文件夹中的所有视频文件
# for video_file in os.listdir(video_folder):
#     if video_file.endswith(".mp4"):  # 只处理 MP4 视频
#         video_path = os.path.join(video_folder, video_file)
        
#         # 假设音频文件与视频文件同名
#         audio_file = video_file.replace(".mp4", ".mp3")
#         audio_path = os.path.join(audio_folder, audio_file)
        
#         # 检查音频文件是否存在
#         if os.path.exists(audio_path):
#             # 加载视频和音频
#             video = VideoFileClip(video_path)
#             audio = AudioFileClip(audio_path)
            
#             # 设置音频到视频
#             video_with_audio = video.set_audio(audio)
            
#             # 输出文件路径
#             output_path = os.path.join(output_folder, video_file)
            
#             # 导出合成的视频
#             video_with_audio.write_videofile(output_path, codec="libx264", audio_codec="aac")
#             print(f"合并完成：{output_path}")
#         else:
#             print(f"音频文件未找到：{audio_path}")