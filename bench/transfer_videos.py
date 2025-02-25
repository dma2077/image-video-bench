import re
import subprocess

# 文件列表
files = [
    "xOqNnbsfq6w.mp4",
    "YBwNA4-O61E.mp4",
    "_w92IZyVJxg.mp4",
    "kToFKqsCVLQ.mp4",
    "eVsXVzSse8I.mp4",
    "k-G_o8FmIWA.mp4",
    "fJUaISAPSVg.mp4",
    "ywUXllHZpcA.mp4",
    "K_ZQkQc9Z2w.mp4",
    "6tCh9ZmiCnA.mp4",
    "SrbxstgqkU0.mp4",
    "qcPtHstIo8I.mp4",
    "MCaeA7-1Ezs.mp4",
    "CBJu_Y_Zjpg.mp4",
    "9tWPZlGZFko.mp4",
    "Gv1N9T5G3rQ.mp4",
    "xv13ECS1vf4.mp4",
    "hfOqREtLmpU.mp4",
    "AjLbe4ZDl0I.mp4",
    "12TC93hh97M.mp4",
    "5ZkdpWNtx58.mp4",
    "ujLgASROJho.mp4",
    "MribRQNEPLQ.mp4",
    "PiQnJyBbx_I.mp4",
    "qL7grOZhEjc.mp4",
    "uyIyi5QwbWc.mp4",
    "q0MxGptN4TY.mp4",
    "Togg5BtfiGc.mp4",
    "E0C3u8sj0tI.mp4",
    "yZ1egVORfn0.mp4",
    "sLrXLCTATYI.mp4",
    "lg5FGYe8CCc.mp4",
    "wUWqBNMYihM.mp4",
    "uLZheW37bxU.mp4",
    "yC7Fl4Ss5Kk.mp4",
    "wJgLNSU_gU4.mp4",
    "wjrCvyOrJpw.mp4"
]

# 目标服务器信息
scp_command_prefix = "scp -P 22544"
remote_directory = "root@101.126.53.52:/map-vepfs/dehua/data/image-video-bench/image-video-bench/youtube_downloads/videos_converted/"

# 执行文件传输
for file in files:
    # 对于文件名中包含 &list= 等字符的情况，进行替换
    cleaned_filename = re.sub(r"&.*\.mp4$", ".mp4", file)
    
    # 生成 SCP 命令
    scp_command = f"{scp_command_prefix} {file} {remote_directory}{cleaned_filename}"
    
    try:
        # 执行 SCP 命令
        print(f"执行命令: {scp_command}")
        subprocess.run(scp_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"文件 {file} 传输失败: {e}")
