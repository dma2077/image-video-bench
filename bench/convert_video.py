import os
import subprocess
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

def convert_video(input_path, output_path, ffmpeg_path="ffmpeg"):
    """
    将单个视频转换为 H.264 格式，并进一步减小文件大小。
    
    Args:
        input_path (str): 输入视频文件的路径。
        output_path (str): 转换后的视频保存路径。
        ffmpeg_path (str): FFmpeg 的路径，默认为 "ffmpeg"。
    """
    # 构造 FFmpeg 命令，进行更多优化
    ffmpeg_command = [
        ffmpeg_path,
        "-i", input_path,          # 输入文件
        "-c:v", "libx264",         # 视频编码器：H.264
        "-preset", "slow",         # 压缩速度与质量的平衡
        "-crf", "23",              # 恒定质量因子，越低越清晰（范围 0-51）
        "-vf", "scale=1280:720",   # 降低分辨率
        "-an",                     # 跳过音频处理（没有音频流时）
        output_path                # 输出文件
    ]
    
    # 执行 FFmpeg 命令
    try:
        subprocess.run(ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 删除原视频文件
        os.remove(input_path)
        print(f"Original video {input_path} has been deleted.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert {input_path}: {e.stderr.decode('utf-8')}")

def process_video_paths(video_paths, ffmpeg_path):
    """
    执行视频转换任务。

    Args:
        video_paths (tuple): 包含输入路径和输出路径的元组。
        ffmpeg_path (str): FFmpeg 的路径。
    """
    input_path, output_path = video_paths
    convert_video(input_path, output_path, ffmpeg_path)

def convert_videos_to_h264(input_dir, output_dir, ffmpeg_path="ffmpeg", max_workers=4):
    """
    将目录中的所有视频转换为 H.264 格式，并保存到另一个目录。使用多进程加速。

    Args:
        input_dir (str): 输入视频目录。
        output_dir (str): 转换后的视频保存目录。
        ffmpeg_path (str): FFmpeg 的路径，默认为 "ffmpeg"。
        max_workers (int): 最大工作进程数，默认 4。
    """
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取输入目录中的所有视频文件
    video_files = [f for f in os.listdir(input_dir) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    
    # 生成输入输出路径
    video_paths = [(os.path.join(input_dir, video), os.path.join(output_dir, video)) for video in video_files]
    
    # 使用多进程执行视频转换
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        list(tqdm(executor.map(process_video_paths, video_paths, [ffmpeg_path]*len(video_paths)), desc="Converting videos", total=len(video_paths)))

    print(f"All videos from {input_dir} have been converted and saved to {output_dir}.")

# 示例使用
if __name__ == "__main__":
    input_directory = "./youtube_downloads/videos"   # 替换为实际输入目录路径
    output_directory = "./youtube_downloads/videos_converted" # 替换为实际输出目录路径
    convert_videos_to_h264(input_directory, output_directory)