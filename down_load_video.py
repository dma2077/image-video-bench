import os
import json
import yt_dlp
import subprocess

# 创建下载文件夹
def create_download_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# 可选：使用 ffprobe 验证文件完整性
def verify_file_integrity(filepath):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_format", "-show_streams", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"验证文件完整性时出错: {e}")
        return False

# 下载视频
def download_youtube_video(video_id, download_folder):
    video_folder = os.path.join(download_folder, "videos")
    create_download_folder(video_folder)

    ydl_opts = {
        "format": "bestvideo[height<=1080][ext=mp4]",
        "outtmpl": os.path.join(video_folder, "%(id)s.%(ext)s"),
        "quiet": False,
        ##"cookies": "/Users/dehua/code/image-video-bench/cookies.json",
        "cookiesfrombrowser": ("chrome",),  # 使用 Chrome 浏览器的 Cookie
        # 增加鲁棒性选项
        "retries": 10,
        "fragment_retries": 10,
        "ignoreerrors": True,
        "continuedl": True,
        "nooverwrites": True,
        "noplaylist": True,
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
        "format": "bestaudio/best",
        "outtmpl": os.path.join(audio_folder, "%(id)s.%(ext)s"),
        "quiet": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        # 增加鲁棒性选项
        "retries": 10,
        "fragment_retries": 10,
        "ignoreerrors": True,
        "continuedl": True,
        "nooverwrites": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)

# 保存元数据到 JSONL 文件
def save_metadata(metadata, metadata_file):
    with open(metadata_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(metadata, ensure_ascii=False) + "\n")

# 收集指定目录下的所有 video id
def collect_video_ids(directory):
    video_ids = []
    for filename in os.listdir(directory):
        if filename.endswith(".jsonl"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                for line in file:
                    data = json.loads(line.strip())
                    if isinstance(data, dict) and len(data) == 1:
                        video_id = list(data.keys())[0]
                        video_ids.append(video_id)
    return video_ids

if __name__ == "__main__":
    # 配置参数
    directory_path = "./res/res_current"  # 存放 .jsonl 文件的目录
    download_folder = "youtube_downloads"
    metadata_file = "metadata.jsonl"
    MAX_RETRIES = 3

    create_download_folder(download_folder)
    all_video_ids = collect_video_ids(directory_path)

    for video_id in all_video_ids:
        for attempt in range(MAX_RETRIES):
            try:
                video_metadata = download_youtube_video(video_id, download_folder)

                metadata = {
                    "cate": video_metadata.get('cate'),
                    "query": video_metadata.get('query'),
                    "uploader": video_metadata.get('uploader'),
                    "uploader_id": video_metadata.get('uploader_id'),
                    "url": video_metadata.get('url'),
                    "video_id": video_metadata.get('video_id'),
                    "title": video_metadata.get('title'),
                    "description": video_metadata.get('description'),
                    "quality": video_metadata.get('quality'),
                    "duration": video_metadata.get('duration'),
                    "publish_time": video_metadata.get('publish_time')
                }
                save_metadata(metadata, metadata_file)

                download_youtube_audio(video_id, download_folder)

                # 可选：验证下载的视频和音频完整性
                video_path = os.path.join(download_folder, "videos", f"{video_id}.mp4")
                audio_path = os.path.join(download_folder, "audios", f"{video_id}.mp3")
                if not verify_file_integrity(video_path):
                    print(f"视频文件 {video_path} 检测失败。")
                if not verify_file_integrity(audio_path):
                    print(f"音频文件 {audio_path} 检测失败。")

                print(f"Downloaded video and audio for: {video_metadata['title']}")
                break  # 成功后跳出重试循环

            except Exception as e:
                print(f"尝试 {attempt + 1}/{MAX_RETRIES} 失败，错误信息: {e}")
                if attempt == MAX_RETRIES - 1:
                    print(f"视频 {video_id} 多次下载失败，跳过。")