import os
import json
import jsonlines

def main():
    # 定义文件路径
    res_current_path = "/Users/dehua/code/image-video-bench/res/res_current"
    video_list_path = "/Users/dehua/code/image-video-bench/text_files/updated_sampled_videos_ids_0109.json"
    missing_videos_output_path = "/Users/dehua/code/image-video-bench/text_files/missing_videos.json"  # 输出全局缺失视频列表的 JSON 文件

    # 读取全局 video id 列表（sampled_video_ids）
    try:
        with open(video_list_path, "r", encoding="utf-8") as f:
            video_list_data = json.load(f)
    except Exception as e:
        print(f"读取 video_list 文件时出错: {e}")
        return

    sampled_video_ids = video_list_data.get("sampled_id", [])
    if not sampled_video_ids:
        print("未在 video_list 文件中找到 'sampled_id' 数据。")
        return

    # 用户映射（原始映射，仅用于获取允许的范围以及排序）
    user_mapping = {
        "dehua1": {"username": "dehua1", "s_idx": 0,   "e_idx": 49,  "current_idx": 42, "video_question_idx": 1},
        "dehua2": {"username": "dehua2", "s_idx": 50,  "e_idx": 99,  "current_idx": 10, "video_question_idx": 2},
        "dehua3": {"username": "dehua3", "s_idx": 100, "e_idx": 149, "current_idx": 0,  "video_question_idx": 0},
        "dehua4": {"username": "dehua4", "s_idx": 150, "e_idx": 199, "current_idx": 25, "video_question_idx": 0},
        "dehua5": {"username": "dehua5", "s_idx": 200, "e_idx": 249, "current_idx": 0,  "video_question_idx": 0},
        "dehua6": {"username": "dehua6", "s_idx": 250, "e_idx": 299, "current_idx": 0,  "video_question_idx": 0},
        "zhongyuan1": {"username": "zhongyuan1", "s_idx": 300, "e_idx": 349, "current_idx": 0,  "video_question_idx": 1},
        "zhongyuan2": {"username": "zhongyuan2", "s_idx": 350, "e_idx": 399, "current_idx": 0,  "video_question_idx": 0},
        "zhongyuan3": {"username": "zhongyuan3", "s_idx": 400, "e_idx": 449, "current_idx": 0,  "video_question_idx": 0},
        "zhongyuan4": {"username": "zhongyuan4", "s_idx": 450, "e_idx": 499, "current_idx": 0,  "video_question_idx": 0},
        "zhongyuan5": {"username": "zhongyuan5", "s_idx": 500, "e_idx": 549, "current_idx": 49, "video_question_idx": 10},
        "zhongyuan6": {"username": "zhongyuan6", "s_idx": 550, "e_idx": 599, "current_idx": 49, "video_question_idx": 1},
        "zhongyuan7": {"username": "zhongyuan7", "s_idx": 600, "e_idx": 649, "current_idx": 0,  "video_question_idx": 0},
        "zhongyuan8": {"username": "zhongyuan8", "s_idx": 650, "e_idx": 699, "current_idx": 0,  "video_question_idx": 0},
        "majun1":    {"username": "majun1",    "s_idx": 700, "e_idx": 749, "current_idx": 3,  "video_question_idx": 1},
        "majun2":    {"username": "majun2",    "s_idx": 750, "e_idx": 799, "current_idx": 0,  "video_question_idx": 0},
        "majun3":    {"username": "majun3",    "s_idx": 800, "e_idx": 849, "current_idx": 2,  "video_question_idx": 0},
        "majun4":    {"username": "majun4",    "s_idx": 850, "e_idx": 899, "current_idx": 48, "video_question_idx": 0},
        "majun5":    {"username": "majun5",    "s_idx": 900, "e_idx": 949, "current_idx": 37, "video_question_idx": 0},
        "majun6":    {"username": "majun6",    "s_idx": 950, "e_idx": 999, "current_idx": 38, "video_question_idx": 0},
        "majun7":    {"username": "majun7",    "s_idx": 1000, "e_idx": 1049, "current_idx": 49, "video_question_idx": 1},
        "majun8":    {"username": "majun8",    "s_idx": 1050, "e_idx": 1099, "current_idx": 30, "video_question_idx": 1},
        "user1":     {"username": "user1",     "s_idx": 1100, "e_idx": 1149, "current_idx": 47, "video_question_idx": 1},
        "user2":     {"username": "user2",     "s_idx": 1150, "e_idx": 1199, "current_idx": 49, "video_question_idx": 1},
        "user3":     {"username": "user3",     "s_idx": 1200, "e_idx": 1249, "current_idx": 0,  "video_question_idx": 0},
        "user4":     {"username": "user4",     "s_idx": 1250, "e_idx": 1299, "current_idx": 11, "video_question_idx": 3},
        "user5":     {"username": "user5",     "s_idx": 1300, "e_idx": 1349, "current_idx": 7,  "video_question_idx": 1},
        "user6":     {"username": "user6",     "s_idx": 1350, "e_idx": 1399, "current_idx": 0,  "video_question_idx": 0},
        "user7":     {"username": "user7",     "s_idx": 1400, "e_idx": 1449, "current_idx": 7,  "video_question_idx": 3},
        "user8":     {"username": "user8",     "s_idx": 1450, "e_idx": 1499, "current_idx": 0,  "video_question_idx": 0},
        "user9":     {"username": "user9",     "s_idx": 1500, "e_idx": 1549, "current_idx": 1,  "video_question_idx": 0},
        "user10":    {"username": "user10",    "s_idx": 1550, "e_idx": 1599, "current_idx": 0,  "video_question_idx": 0},
        "user11":    {"username": "user11",    "s_idx": 1600, "e_idx": 1649, "current_idx": 0,  "video_question_idx": 0},
        "user12":    {"username": "user12",    "s_idx": 1650, "e_idx": 1699, "current_idx": 15, "video_question_idx": 0},
        "user13":    {"username": "user13",    "s_idx": 1700, "e_idx": 1749, "current_idx": 0,  "video_question_idx": 0},
        "user14":    {"username": "user14",    "s_idx": 1750, "e_idx": 1799, "current_idx": 7,  "video_question_idx": 0},
        "user15":    {"username": "user15",    "s_idx": 1800, "e_idx": 1833, "current_idx": 0,  "video_question_idx": 0},
        "user16":    {"username": "user16",    "s_idx": 1834, "e_idx": 1862, "current_idx": 0,  "video_question_idx": 0},
        "user17":    {"username": "user17",    "s_idx": 1863, "e_idx": 1876, "current_idx": 0,  "video_question_idx": 0},
        "user18":    {"username": "user18",    "s_idx": 1950, "e_idx": 1999, "current_idx": 0,  "video_question_idx": 0},
    }

    # ================================
    # 第一步：遍历 res_current 下的 JSONL 文件，统计每个用户缺失的 video id
    # ================================
    missing_videos_mapping = {}  # 记录每个用户缺失的视频（以集合形式，后续会排序）

    for filename in os.listdir(res_current_path):
        if not filename.endswith(".jsonl"):
            continue

        file_path = os.path.join(res_current_path, filename)
        file_video_ids = set()
        try:
            with jsonlines.open(file_path, "r") as reader:
                for obj in reader:
                    if isinstance(obj, dict):
                        # 假设每个字典的键为 video id
                        file_video_ids.update(obj.keys())
        except Exception as e:
            print(f"读取文件 {filename} 时出错: {e}")
            continue

        # 根据文件名确定对应的用户（如果文件名以 "ans_" 开头，则去掉该前缀）
        base_name = filename.split(".")[0]
        user_key = base_name[4:] if base_name.startswith("ans_") else base_name

        if user_key not in user_mapping:
            print(f"文件 {filename} 对应的用户 {user_key} 不在 user_mapping 中，跳过。")
            continue

        # 根据 user_mapping 获取该用户允许的视频范围
        s_idx_user = user_mapping[user_key]["s_idx"]
        e_idx_user = user_mapping[user_key]["e_idx"]
        allowed_videos = set(sampled_video_ids[s_idx_user: e_idx_user + 1])
        missing_ids = file_video_ids - allowed_videos

        if missing_ids:
            missing_videos_mapping.setdefault(user_key, set()).update(missing_ids)

    # 对每个用户缺失的视频按全局 video 列表中的顺序排序
    def sort_key(video_id):
        try:
            return (0, sampled_video_ids.index(video_id))
        except ValueError:
            return (1, video_id)

    for user in missing_videos_mapping:
        missing_videos_mapping[user] = sorted(missing_videos_mapping[user], key=sort_key)

    # ================================
    # 第二步：将所有用户缺失的视频拼接成一个全局列表，并构造 missing_user_mapping
    # ================================
    global_missing_list = []
    missing_user_mapping = {}  # 键为用户名，值为 {"username": user, "s_idx": 起始索引, "e_idx": 结束索引}

    # 按照 user_mapping 的 s_idx 排序用户（保证输出顺序与原映射一致）
    sorted_users = sorted(user_mapping.keys(), key=lambda u: user_mapping[u]["s_idx"])
    for user in sorted_users:
        missing_list = missing_videos_mapping.get(user, [])
        if missing_list:
            start_index = len(global_missing_list)
            global_missing_list.extend(missing_list)
            end_index = len(global_missing_list) - 1
            missing_user_mapping[user] = {"username": user, "s_idx": start_index, "e_idx": end_index}
        else:
            # 若该用户没有缺失视频，可将 s_idx 与 e_idx 置为 None（也可不加入该用户）
            missing_user_mapping[user] = {"username": user, "s_idx": None, "e_idx": None}

    # ================================
    # 第三步：将全局缺失视频列表写入 JSON 文件（键为 "sampled_id"）
    # ================================
    output_data = {"sampled_id": global_missing_list}
    try:
        with open(missing_videos_output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        print(f"缺失的视频列表已写入 {missing_videos_output_path}")
    except Exception as e:
        print(f"写入缺失视频文件时出错: {e}")

    # 输出 missing_user_mapping 结果（可用于后续映射）
    print("missing_user_mapping:")
    print(json.dumps(missing_user_mapping, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
