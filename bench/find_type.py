import os
import json

# 指定 JSONL 文件所在目录
directory = "/Users/dehua/code/image-video-bench/res/res_current"

# 假设这是视频索引列表，需替换为真实列表

with open("/Users/dehua/code/image-video-bench/text_files/missing_videos.json", 'r') as file:
    data = json.load(file)

video_list = data["sampled_id"]  # 你的视频 ID 列表

with open("/Users/dehua/code/image-video-bench/text_files/missing_user_info.json", 'r') as file:
    user_video_mapping = json.load(file)

# # 用户索引映射字典
# user_video_mapping = {
#     "dehua1": {"s_idx": 0, "e_idx": 49},
#     "dehua2": {"s_idx": 50, "e_idx": 99},
#     "dehua3": {"s_idx": 100, "e_idx": 149},
#     "dehua4": {"s_idx": 150, "e_idx": 199},
#     "dehua5": {"s_idx": 200, "e_idx": 249},
#     "dehua6": {"s_idx": 250, "e_idx": 299},
#     "zhongyuan1": {"s_idx": 300, "e_idx": 349},
#     "zhongyuan2": {"s_idx": 350, "e_idx": 399},
#     "zhongyuan3": {"s_idx": 400, "e_idx": 449},
#     "zhongyuan4": {"s_idx": 450, "e_idx": 499},
#     "zhongyuan5": {"s_idx": 500, "e_idx": 549},
#     "zhongyuan6": {"s_idx": 550, "e_idx": 599},
#     "zhongyuan7": {"s_idx": 600, "e_idx": 649},
#     "zhongyuan8": {"s_idx": 650, "e_idx": 699},
#     "majun1": {"s_idx": 700, "e_idx": 749},
#     "majun2": {"s_idx": 750, "e_idx": 799},
#     "majun3": {"s_idx": 800, "e_idx": 849},
#     "majun4": {"s_idx": 850, "e_idx": 899},
#     "majun5": {"s_idx": 900, "e_idx": 949},
#     "majun6": {"s_idx": 950, "e_idx": 999},
#     "majun7": {"s_idx": 1000, "e_idx": 1049},
#     "majun8": {"s_idx": 1050, "e_idx": 1099},
#     "user1": {"s_idx": 1100, "e_idx": 1149},
#     "user2": {"s_idx": 1150, "e_idx": 1199},
#     "user3": {"s_idx": 1200, "e_idx": 1249},
#     "user4": {"s_idx": 1250, "e_idx": 1299},
#     "user5": {"s_idx": 1300, "e_idx": 1349},
#     "user6": {"s_idx": 1350, "e_idx": 1399},
#     "user7": {"s_idx": 1400, "e_idx": 1449},
#     "user8": {"s_idx": 1450, "e_idx": 1499},
#     "user9": {"s_idx": 1500, "e_idx": 1549},
#     "user10": {"s_idx": 1550, "e_idx": 1599},
#     "user11": {"s_idx": 1600, "e_idx": 1649},
#     "user12": {"s_idx": 1650, "e_idx": 1699},
#     "user13": {"s_idx": 1700, "e_idx": 1749},
#     "user14": {"s_idx": 1750, "e_idx": 1799},
#     "user15": {"s_idx": 1800, "e_idx": 1833},
#     "user16": {"s_idx": 1834, "e_idx": 1862},
#     "user17": {"s_idx": 1863, "e_idx": 1876},
#     "user18": {"s_idx": 1877, "e_idx": 1912},
# }

# 存储符合条件的记录
results = []

# 遍历目录中的 JSONL 文件
for filename in os.listdir(directory):
    if filename.endswith(".jsonl"):
        file_path = os.path.join(directory, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                try:
                    data = json.loads(line.strip())  # 去除首尾空白字符，确保 JSON 结构
                except json.JSONDecodeError as e:
                    print(f"JSON 解析错误：{file_path}, 行号 {line_number}, 错误: {e}")
                    continue  # 跳过当前行，继续解析下一个 JSONL
                for video_id, entries in data.items():
                    for entry in entries:
                        if entry["question_type"] in ["Summary", "Instruction manual"]:
                            data_id = entry["data_id"]
                            # 获取视频索引
                            if video_id in video_list:
                                video_idx = video_list.index(video_id)
                                # 找到所属用户
                                for username, info in user_video_mapping.items():
                                    if info["s_idx"] and info["e_idx"]:
                                        if info["s_idx"] <= video_idx <= info["e_idx"]:
                                            video_relative_idx = video_idx - info["s_idx"] + 1
                                            results.append(f"{username}-{video_relative_idx}-{data_id}")
                                            break

# 输出结果
for res in results:
    print(res)
