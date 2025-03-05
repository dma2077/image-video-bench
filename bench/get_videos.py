import json

category_filename = "/Users/dehua/code/image-video-bench/res/video_category.json"
with open(category_filename, 'r', encoding='utf-8') as file:
    category = json.load(file)

category_filename = "/Users/dehua/code/image-video-bench/res/all_data_v3.jsonl"
video_list = []
with open(category_filename, 'r', encoding='utf-8') as file:
    for data in file.readlines():
        data = json.loads(data)
        for k, v in data.items():
            video_list.append(k)


# video_list = []
# for k, v in category.items():
#     video_list.append(k)

# video_ids_filename = "/Users/dehua/code/image-video-bench/text_files/videos_0305.json"
# data = {"sampled_id": []}
# with open(video_ids_filename, 'w', encoding='utf-8') as file:
#     data["sampled_id"] = video_list
#     json.dump(data, file, indent=4)
data_filename = "/Users/dehua/code/image-video-bench/res/res_current/ans_user21.jsonl"
data_filename1 = "/Users/dehua/code/image-video-bench/res/res_current/ans_user22.jsonl"
template = {'data_id': 0, 'image_name': '', 'question': '', 'question_type': '', 'granularity': '', 'answer': '', 'answer_location': '', 'distractors': ['', '', '', '', '', '', '', '', '']}
datas = []
with open(data_filename, 'w', encoding='utf-8') as file:
    for video in video_list[:501]:
        if video in category:
            v = category[video]
        else:
            v = ""
        if v == "knowledge":
            v = "Knowledge Dissemination"
        if v == "Sports":
            v = "Sports Competition"
        if v == "file_and_tv":
            v = "Film and Television"
        if v == "Arts and Performance":
            v = "Artistic Performance"
        if v == "Life Records":
            v = "Life Record"
        template["question_type"] = v
        template_list = [template]
        data = {
            video: template_list
        }
        data = json.dumps(data)
        file.write(data)
        file.write('\n')

with open(data_filename1, 'w', encoding='utf-8') as file:
    for video in video_list[501:]:
        if video in category:
            v = category[video]
        else:
            v = ""
        if v == "knowledge":
            v = "Knowledge Dissemination"
        if v == "Sports":
            v = "Sports Competition"
        if v == "file_and_tv":
            v = "Film and Television"
        if v == "Arts and Performance":
            v = "Artistic Performance"
        if v == "Life Records":
            v = "Life Record"
        template["question_type"] = v
        template_list = [template]
        data = {
            video: template_list
        }
        data = json.dumps(data)
        file.write(data)
        file.write('\n')