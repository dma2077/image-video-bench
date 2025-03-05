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
    video_path = os.path.join(video_folder, f"{video_id}.mp4")

    # 1. 前检测：如果文件已存在，则直接返回占位的元数据，跳过所有下载操作（包括 cookies 读取）
    if os.path.exists(video_path):
        print(f"视频文件已存在，跳过下载：{video_path}")
        return {
            "cate": None,
            "query": None,
            "uploader": None,
            "uploader_id": None,
            "url": None,
            "video_id": video_id,
            "title": "已存在的视频，未获取新元数据",
            "description": "",
            "quality": "",
            "duration": 0,
            "publish_time": "",
        }

    # 2. 如果文件不存在，则执行原有逻辑
    ydl_opts = {
        "format": "bestvideo[height<=1080][ext=mp4]",
        "outtmpl": os.path.join(video_folder, "%(id)s.%(ext)s"),
        "quiet": False,
        #"cookies": "/Users/dehua/code/image-video-bench/cookies.txt",  # 如有需要可保留
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
    audio_path = os.path.join(audio_folder, f"{video_id}.mp3")

    # 1. 前检测：如果文件已存在，则直接返回，跳过所有下载操作（包括 cookies 读取）
    if os.path.exists(audio_path):
        print(f"音频文件已存在，跳过下载：{audio_path}")
        return

    # 2. 如果文件不存在，则执行原有逻辑
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

def collect_video_ids(directory, video_dir_1, video_dir_2):
    video_ids = []
    
    # 获取第一个下载目录中已经存在的视频文件名（去掉扩展名）
    existing_videos = {os.path.splitext(f)[0] for f in os.listdir(video_dir_1) if os.path.isfile(os.path.join(video_dir_1, f))}
    
    # 获取第二个下载目录中已经存在的视频文件名（去掉扩展名）
    existing_videos.update({os.path.splitext(f)[0] for f in os.listdir(video_dir_2) if os.path.isfile(os.path.join(video_dir_2, f))})
    
    if directory.endswith(".jsonl"):
        filepath = os.path.join(directory, filename)
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                data = json.loads(line.strip())
                if isinstance(data, dict) and len(data) == 1:
                    video_id = list(data.keys())[0]
                    
                    # 只有当视频文件不存在时，才加入列表
                    if video_id not in existing_videos:
                        video_ids.append(video_id)
    else:
        # 遍历 JSONL 文件
        for filename in os.listdir(directory):
            if filename.endswith(".jsonl"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r", encoding="utf-8") as file:
                    for line in file:
                        data = json.loads(line.strip())
                        if isinstance(data, dict) and len(data) == 1:
                            video_id = list(data.keys())[0]
                            
                            # 只有当视频文件不存在时，才加入列表
                            if video_id not in existing_videos:
                                video_ids.append(video_id)
    
    return video_ids


if __name__ == "__main__":
    # 配置参数
    directory_path = "./res/res_current"  # 存放 .jsonl 文件的目录
    download_folder = "youtube_downloads"
    metadata_file = "metadata.jsonl"
    MAX_RETRIES = 3
    video_dir1 = "/Users/dehua/code/image-video-bench/youtube_downloads/videos"
    video_dir2 = "/Users/dehua/code/image-video-bench/youtube_downloads/videos_converted"
    create_download_folder(download_folder)
    all_video_ids = collect_video_ids(directory_path, video_dir1, video_dir2)
    all_video_ids = ['bgrhfIkC1R4']
    for video_id in all_video_ids:
        for attempt in range(MAX_RETRIES):
            try:
                # 1. 下载并获取视频元数据（如果视频已存在则不会再次下载，会直接返回占位信息）
                video_metadata = download_youtube_video(video_id, download_folder)

                # 2. 组装/保存元数据
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

                # 3. 下载音频（如果音频已存在则不会再次下载）
                download_youtube_audio(video_id, download_folder)

                # 4. 可选：验证下载的视频和音频完整性
                video_path = os.path.join(download_folder, "videos", f"{video_id}.mp4")
                audio_path = os.path.join(download_folder, "audios", f"{video_id}.mp3")

                if os.path.exists(video_path) and not verify_file_integrity(video_path):
                    print(f"视频文件 {video_path} 检测失败。")
                if os.path.exists(audio_path) and not verify_file_integrity(audio_path):
                    print(f"音频文件 {audio_path} 检测失败。")

                print(f"已处理视频 ID: {video_id}，标题: {video_metadata['title']}")
                break  # 成功后跳出重试循环

            except Exception as e:
                print(f"尝试 {attempt + 1}/{MAX_RETRIES} 失败，错误信息: {e}")
                if attempt == MAX_RETRIES - 1:
                    print(f"视频 {video_id} 多次下载失败，跳过。")
