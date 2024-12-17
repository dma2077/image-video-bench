import yt_dlp
import os
import json


# 创建下载文件夹
def create_download_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


# 下载视频
def download_youtube_video(video_id, download_folder):
    video_folder = os.path.join(download_folder, "videos")
    create_download_folder(video_folder)

    ydl_opts = {
        "format": "bestvideo[height<=1080][ext=mp4]",  # 下载最佳 MP4 格式视频
        "outtmpl": os.path.join(video_folder, "%(id)s.%(ext)s"),  # 设置保存文件名
        "quiet": False,  # 输出详细信息
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(
            f"https://www.youtube.com/watch?v={video_id}", download=True
        )
        return {
            "cate": result.get("categories", None),
            "query": result.get("query", None),
            "uploader": result.get("uploader", None),
            "uploader_id": result.get("uploader_id", None),
            "url": result.get("webpage_url", None),
            "video_id": video_id,
            "title": result.get("title", "Unknown title"),
            "description": result.get("description", ""),
            "quality": result.get("resolution", "Unknown quality"),
            "duration": result.get("duration", 0),
            "publish_time": result.get("upload_date", "Unknown date"),
        }


# 下载音频
def download_youtube_audio(video_id, download_folder):
    audio_folder = os.path.join(download_folder, "audios")
    create_download_folder(audio_folder)

    ydl_opts = {
        "format": "bestaudio/best",  # 下载最佳音频
        "outtmpl": os.path.join(audio_folder, "%(id)s.%(ext)s"),  # 设置保存文件名
        "quiet": False,  # 输出详细信息
        "postprocessors": [
            {  # 转换音频为 MP3 格式
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)


# 保存元数据到 JSONL 文件
def save_metadata(metadata, metadata_file):
    with open(metadata_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(metadata, ensure_ascii=False) + "\n")


# if __name__ == "__main__":
#     video_ids = []
#     with open('/map-vepfs/dehua/data/image-video-bench/image-video-bench/sample_video_ids_1222.txt', 'r', encoding='utf-8') as file:
#         for line in file.readlines():
#             video_ids.append(line.strip())
#     download_folder = "youtube_downloads"
#     metadata_file = "metadata.jsonl"
#     create_download_folder(download_folder)

#     for video_id in video_ids:
#         try:
#             video_metadata = download_youtube_video(video_id, download_folder)

#             # 保存单一元数据格式
#             metadata = {
#                 "cate": video_metadata.get('cate'),
#                 "query": video_metadata.get('query'),
#                 "uploader": video_metadata.get('uploader'),
#                 "uploader_id": video_metadata.get('uploader_id'),
#                 "url": video_metadata.get('url'),
#                 "video_id": video_metadata.get('video_id'),
#                 "title": video_metadata.get('title'),
#                 "description": video_metadata.get('description'),
#                 "quality": video_metadata.get('quality'),
#                 "duration": video_metadata.get('duration'),
#                 "publish_time": video_metadata.get('publish_time')
#             }
#             save_metadata(metadata, metadata_file)

#             download_youtube_audio(video_id, download_folder)

#             print(f"Downloaded video and audio for: {video_metadata['title']}")

#         except Exception as e:
#             print(f"捕获到异常: {e}")  # 输出错误信息


################合并音频和视频################
import os
import subprocess

# 文件路径
audio_folder = r"/map-vepfs/dehua/data/image-video-bench/image-video-bench/youtube_downloads/audios"
video_folder = r"/map-vepfs/dehua/data/image-video-bench/image-video-bench/youtube_downloads/videos"
output_folder = r"/map-vepfs/dehua/data/image-video-bench/image-video-bench/youtube_downloads/outputs"

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 获取音频和视频文件列表
audio_files = {
    os.path.splitext(f)[0]: audio_folder + "/" + f
    for f in os.listdir(audio_folder)
    if f.endswith(".mp3")
}
video_files = {
    os.path.splitext(f)[0]: video_folder + "/" + f
    for f in os.listdir(video_folder)
    if f.endswith(".mp4")
}

# ffmpeg的完整路径
# ffmpeg_path = r"E:/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"
# ffmpeg的完整路径
ffmpeg_path = "/usr/bin/ffmpeg"

# 合并音频和视频
for name, video_path in video_files.items():
    if name in audio_files:
        audio_path = audio_files[name]
        output_path = output_folder + "/" + f"{name}.mp4"
        if os.path.exists(output_path):  # 修正为 os.path.exists
            print(f"{output_path} already exists")  # 文本表达更标准
            continue
        print(f"Processing: {name}")

        cmd = [
            ffmpeg_path,
            "-y",  # 覆盖输出文件而不提示
            "-i",
            video_path,
            "-i",
            audio_path,
            # "-map", "0:v:0",    # 选择第一个输入的第一个视频流
            # "-map", "1:a:0",    # 选择第二个输入的第一个音频流
            "-c:v",
            "copy",  # 复制视频流，不重新编码
            "-c:a",
            "aac",  # 使用AAC编码音频
            "-shortest",  # 使输出长度与最短的输入流一致
            output_path,
        ]

        try:
            # 执行ffmpeg命令并捕获输出
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print(f"Output saved: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing {name}:")
            print(e.stderr)

print("All files processed successfully.")
