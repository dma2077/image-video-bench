from huggingface_hub import snapshot_download

# 下载指定的文件


local_path = 'E:\Code\image-video-bench'
# 下载整个仓库的特定部分（webpage_v2）
repo_dir = snapshot_download(
    repo_id="hexuan21/VideoScore_legacy",  # 替换为你的仓库名
    cache_dir=local_path,                  # 指定保存路径
    allow_patterns=["webpage_v2/**"],       # 只下载 webpage_v2 目录
    repo_type='dataset'
)

print(f"文件已下载到: {repo_dir}")
