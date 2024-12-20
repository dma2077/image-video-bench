import os
import json
import math
import time
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langdetect import detect, LangDetectException  # 新增：引入语言检测库

# 替换为您的YouTube Data API密钥
API_KEY = 'AIzaSyCmmSEU_kAxwGERrwxmVTS068tTK71T6l4'

# 按时长分类的约束条件（每个类别）
duration_constraints = {
    '5-10': 26,    # 每个类别选择26个5-10分钟的视频
    '10-30': 7,    # 每个类别选择7个10-30分钟的视频
    '30+': 3       # 每个类别选择3个30分钟以上的视频
}

# 总视频数量
total_videos = 1100

# 初始化YouTube Data API客户端
youtube = build('youtube', 'v3', developerKey=API_KEY)

# 创建下载文件夹（用于组织视频路径）
def create_download_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# 获取YouTube支持的所有类别
def get_all_youtube_categories(region_code='US'):
    categories = {}
    try:
        request = youtube.videoCategories().list(
            part='snippet',
            regionCode=region_code
        )
        response = request.execute()
        for item in response.get('items', []):
            category_title = item['snippet']['title'].strip()
            categories[category_title] = item['id']
    except HttpError as e:
        print(f"HTTP错误发生: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    return categories

# 将ISO 8601格式的时长转换为分钟
def iso8601_duration_to_minutes(duration):
    pattern = re.compile(
        'P'  # starts with 'P'
        '(?:(?P<years>\d+)Y)?'
        '(?:(?P<months>\d+)M)?'
        '(?:(?P<weeks>\d+)W)?'
        '(?:(?P<days>\d+)D)?'
        '(?:T'  # Time part begins with 'T'
        '(?:(?P<hours>\d+)H)?'
        '(?:(?P<minutes>\d+)M)?'
        '(?:(?P<seconds>\d+)S)?'
        ')?'
    )
    match = pattern.match(duration)
    if not match:
        return 0
    parts = match.groupdict()
    time_in_minutes = 0
    if parts['years']:
        time_in_minutes += int(parts['years']) * 525600
    if parts['months']:
        time_in_minutes += int(parts['months']) * 43800
    if parts['weeks']:
        time_in_minutes += int(parts['weeks']) * 10080
    if parts['days']:
        time_in_minutes += int(parts['days']) * 1440
    if parts['hours']:
        time_in_minutes += int(parts['hours']) * 60
    if parts['minutes']:
        time_in_minutes += int(parts['minutes'])
    if parts['seconds']:
        time_in_minutes += int(int(parts['seconds']) / 60)
    return time_in_minutes

# 语言检测函数，判断文本是否为英文
def is_english(text):
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False

# 获取视频详情
def get_video_details(video_ids):
    details = []
    try:
        for i in range(0, len(video_ids), 50):
            request = youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(video_ids[i:i+50])
            )
            response = request.execute()
            details.extend(response.get('items', []))
            time.sleep(0.1)  # 避免超出配额限制
    except HttpError as e:
        print(f"HTTP错误发生: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    return details

# 获取每个类别的视频ID并分类
def get_videos_by_category(category_id, constraint, total_videos):
    video_ids = {
        '5-10': [],
        '10-30': [],
        '30+': []
    }
    try:
        next_page_token = None
        while any(len(video_ids[key]) < constraint[key] for key in constraint) and (len(video_ids['5-10']) + len(video_ids['10-30']) + len(video_ids['30+'])) < total_videos:
            request = youtube.search().list(
                part='id',
                type='video',
                videoCategoryId=category_id,
                maxResults=50,
                order='date',
                videoDuration='any',  # 我们将在代码中根据时长进行过滤
                pageToken=next_page_token
            )
            response = request.execute()
            ids = [item['id']['videoId'] for item in response.get('items', [])]
            if not ids:
                break
            details = get_video_details(ids)
            for detail in details:
                vid = detail['id']
                duration_iso = detail['contentDetails']['duration']
                duration = iso8601_duration_to_minutes(duration_iso)
                # 过滤总时长低于5分钟的视频
                if duration < 5:
                    continue
                # 根据时长分类
                if 5 <= duration <= 10 and len(video_ids['5-10']) < constraint['5-10']:
                    video_ids['5-10'].append(vid)
                elif 10 < duration <= 30 and len(video_ids['10-30']) < constraint['10-30']:
                    video_ids['10-30'].append(vid)
                elif duration > 30 and len(video_ids['30+']) < constraint['30+']:
                    video_ids['30+'].append(vid)
                # 检查是否达到总需求
                total_collected = len(video_ids['5-10']) + len(video_ids['10-30']) + len(video_ids['30+'])
                if total_collected >= total_videos:
                    break
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
    except HttpError as e:
        print(f"HTTP错误发生: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    # 合并所有视频ID
    all_ids = video_ids['5-10'] + video_ids['10-30'] + video_ids['30+']
    return all_ids

# 获取所有视频的元数据
def get_metadata_for_videos(video_ids, category_name, download_folder):
    metadata_list = []
    try:
        details = get_video_details(video_ids)
        for detail in details:
            vid = detail['id']
            duration_iso = detail['contentDetails']['duration']
            duration = iso8601_duration_to_minutes(duration_iso)
            # 再次过滤总时长低于5分钟的视频
            if duration < 5:
                continue
            # 判断清晰度
            definition = detail['contentDetails'].get('definition', 'unknown').lower()
            if definition not in ['hd', 'full']:
                # 非HD或Full清晰度可能低于1080p
                continue
            # 获取标题、描述和上传者
            title = detail['snippet'].get('title', '')
            description = detail['snippet'].get('description', '')
            uploader = detail['snippet'].get('channelTitle', '')
            # 检测语言是否为英文
            if not (is_english(title) and is_english(description) and is_english(uploader)):
                continue  # 如果任意一个元素不是英文，则跳过该视频
            # 构建视频路径，确保使用download_folder
            video_path = os.path.join(download_folder, "videos", category_name.replace(" ", "_"), f"{vid}.mp4")
            metadata = {
                "category": category_name,
                "cate": detail.get("categoryId", None),
                "query": None,  # YouTube Data API没有直接的查询参数
                "uploader": uploader,
                "uploader_id": detail['snippet'].get("channelId", None),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "video_id": vid,
                "title": title if title else "Unknown title",
                "description": description,
                "quality": definition,
                "duration": duration,
                "publish_time": detail['snippet'].get("publishedAt", "Unknown date"),
                "video_path": video_path
            }
            metadata_list.append(metadata)
        time.sleep(0.1)  # 避免超出配额限制
    except HttpError as e:
        print(f"HTTP错误发生: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    return metadata_list

# 保存元数据到 JSONL 文件
def save_metadata(metadata, metadata_file):
    with open(metadata_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(metadata, ensure_ascii=False) + "\n")

# 主函数
if __name__ == "__main__":
    download_folder = "youtube_downloads"
    metadata_file = "metadata_new.jsonl"
    create_download_folder(download_folder)

    # 获取YouTube支持的类别
    print("获取YouTube支持的类别...")
    youtube_categories = get_all_youtube_categories(region_code='US')  # 可根据需要更改区域代码
    print(f"找到 {len(youtube_categories)} 个YouTube类别。")

    if not youtube_categories:
        print("未找到任何YouTube类别，脚本终止。")
        exit()

    num_categories = len(youtube_categories)
    # 计算每个类别需要的总视频数量
    videos_per_category_total = math.floor(total_videos / num_categories)
    remaining_videos = total_videos - (videos_per_category_total * num_categories)

    # 按比例调整每个类别的约束条件
    # 将 duration_constraints 按比例分配到每个类别
    per_category_constraints = {}
    total_duration_constraints = sum(duration_constraints.values())  # 36
    for category in youtube_categories.keys():
        per_category_constraints[category] = {
            '5-10': math.floor(duration_constraints['5-10'] * videos_per_category_total / total_duration_constraints),
            '10-30': math.floor(duration_constraints['10-30'] * videos_per_category_total / total_duration_constraints),
            '30+': math.floor(duration_constraints['30+'] * videos_per_category_total / total_duration_constraints)
        }

    # 处理剩余视频
    # 按照 '5-10', '10-30', '30+' 的比例分配剩余视频
    duration_order = ['5-10', '10-30', '30+']
    for _ in range(remaining_videos):
        for key in duration_order:
            # 随机选择一个类别来分配剩余视频
            # 这里为了简单起见，分配到每个类别的相应分类中
            # 可以根据需要更改分配逻辑
            for category in youtube_categories.keys():
                per_category_constraints[category][key] += 1
                break  # 每次只分配一个视频
            break  # 每次只分配一个视频
        # 减少剩余视频计数
        remaining_videos -=1
        if remaining_videos ==0:
            break

    print("每个类别将分配如下视频数量（按时长分类）：")
    # 只显示前5个类别以避免大量输出
    for cat, cons in list(per_category_constraints.items())[:5]:
        print(f"类别 '{cat}': {cons}")
    if len(per_category_constraints) >5:
        print("...")

    all_metadata = []
    category_counter = 0

    # 获取每个类别的视频ID并获取元数据
    for category_name, category_id in youtube_categories.items():
        category_counter += 1
        print(f"正在处理类别 {category_counter}/{len(youtube_categories)}: '{category_name}' (ID: {category_id})")
        constraints = per_category_constraints[category_name]
        total_videos_per_cat = sum(constraints.values())
        video_ids = get_videos_by_category(category_id, constraints, total_videos_per_cat)
        print(f"找到 {len(video_ids)} 个视频ID。")

        # 获取视频元数据
        metadata_list = get_metadata_for_videos(video_ids, category_name, download_folder)
        print(f"收集到 {len(metadata_list)} 个视频的元数据。")

        # 创建类别文件夹（仅元数据）
        category_folder = os.path.join(download_folder, "videos", category_name.replace(" ", "_"))
        create_download_folder(category_folder)

        # 保存元数据
        for metadata in metadata_list:
            save_metadata(metadata, metadata_file)
            all_metadata.append(metadata)

    # 检查总视频数
    print(f"总共收集到 {len(all_metadata)} 个视频的元数据。")

    # 如果总数不足1100，根据需要进行调整（例如，随机补充）
    if len(all_metadata) < total_videos:
        print(f"总视频数不足1100，仅收集到 {len(all_metadata)} 个视频。")
        # 可根据需要添加补充逻辑
    else:
        print("所有任务完成！")
