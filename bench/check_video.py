import os
import subprocess
import json
from tqdm import tqdm  # 引入 tqdm 库

# 定义一个函数来写入错误日志到文件
def log_error_to_file(error_message, log_file='error_videos.txt'):
    with open(log_file, 'a') as f:
        f.write(f"{error_message}\n")

# 定义检查视频文件的函数
def check_video_file(video_file, log_file='error_videos.txt'):
    try:
        # 使用 ffprobe 检查视频流信息
        ffprobe_command = [
            'ffprobe', '-v', 'error', '-show_entries', 'stream=index,codec_type', 
            '-of', 'json', video_file
        ]
        ffprobe_output = subprocess.check_output(ffprobe_command, stderr=subprocess.PIPE)
        streams_info = json.loads(ffprobe_output)
        
        # 查找视频流（索引为 0 的流通常是视频流）
        video_stream_found = False
        for stream in streams_info['streams']:
            if stream['codec_type'] == 'video':
                video_stream_found = True
                break
        
        # 如果没有找到视频流，说明该视频文件只有音频流或文件损坏
        if not video_stream_found:
            error_message = f"[ERROR] No video stream found in: {video_file}"
            print(error_message)
            log_error_to_file(error_message, log_file)
            return False

        # 使用 ffmpeg 尝试解码视频，捕获错误
        ffmpeg_command = ['ffmpeg', '-v', 'error', '-i', video_file, '-f', 'null', '-']
        subprocess.check_call(ffmpeg_command, stderr=subprocess.PIPE)
        
        print(f"[INFO] Successfully decoded: {video_file}")
        return True

    except subprocess.CalledProcessError as e:
        # 捕获并打印错误信息
        stderr = e.stderr.decode('utf-8')
        
        # 检查是否包含 mmco 或流索引错误
        if 'mmco: unref short failure' in stderr:
            error_message = f"[ERROR] mmco: unref short failure in: {video_file}"
            print(error_message)
            log_error_to_file(error_message, log_file)
        elif 'ERROR cannot find video stream with wanted index: -1' in stderr:
            error_message = f"[ERROR] Cannot find video stream in: {video_file}"
            print(error_message)
            log_error_to_file(error_message, log_file)
        else:
            error_message = f"[ERROR] FFmpeg error while processing {video_file}: {stderr}"
            print(error_message)
            log_error_to_file(error_message, log_file)
        return False

# 遍历目录，检查所有视频文件
def check_videos_in_directory(directory, log_file='error_videos.txt'):
    # 清空日志文件，确保每次运行是新的日志
    open(log_file, 'w').close()

    # 获取所有视频文件列表
    video_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv')):  # 只处理视频文件
                video_files.append(os.path.join(root, file))

    # 使用 tqdm 显示进度条
    for video_file in tqdm(video_files, desc="Processing Videos", ncols=100):
        print(f"[INFO] Checking video: {video_file}")
        check_video_file(video_file, log_file)

if __name__ == "__main__":
    # 设置要检查的目录路径
    directory_to_check = '/Users/dehua/code/image-video-bench/youtube_downloads/videos_converted'  # 需要检查的视频文件夹路径
    log_file = '/Users/dehua/code/image-video-bench/youtube_downloads/error_videos.txt'  # 错误日志文件路径
    check_videos_in_directory(directory_to_check, log_file)