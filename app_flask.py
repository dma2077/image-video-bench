from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from datetime import timedelta
import json
import datetime
import os
from werkzeug.utils import secure_filename
import uuid
import markdown
import shutil

# ======== static and global variables ========
static_root_path = "./videos"
# static_root_path = "E:/Code/image-video-bench/videos"

app = Flask(__name__, static_folder=static_root_path)
app.secret_key = os.urandom(24)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=100)
PORT_NUM = 22005
subpath = "/image_video_bench/"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "welcome"

local_video_dir = "./examples/youtube_sampled"
res_dir = "./res/res_current"
text_files_dir = "text_files"
text_en_path = f"./{text_files_dir}/text_en_display.jsonl"
text_zh_path = f"./{text_files_dir}/text_zh_display.jsonl"
user_info_path = f"./{text_files_dir}/user_info.json"
user_question_type_info_path = f"./{text_files_dir}/user_question_type_info.json"

reported_problem_log = f"./{text_files_dir}/problem_reported.json"
sampled_id_file = f"./{text_files_dir}/updated_sampled_videos_ids_0109.json"


title_template_file = f"./{text_files_dir}/annonation_template.json"
distractors_template_file = f"./{text_files_dir}/distractors_template.json"

with open(title_template_file, "r", encoding="utf-8") as f:
    title_template_data = json.load(f)
with open(distractors_template_file, "r", encoding="utf-8") as f:
    distractors_template_data = json.load(f)



# 替换 title_template_data 中的 Undefined 或 None 值
def clean_data(data):
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data(v) for v in data]
    elif data is None:  # 你也可以根据需要修改这里
        return ""  # 替换为适当的默认值
    return data


title_template_data = clean_data(json.dumps(title_template_data, ensure_ascii=False))
# title_template_data = json.dumps(title_template_data, ensure_ascii="flase")
distractors_template_data = clean_data(json.dumps(distractors_template_data, ensure_ascii=False))

# ======== preparing video-ids and videos  =========
video_id_list = []
videos = []

with open(sampled_id_file, "r", encoding="utf-8") as f:
    sampled_id_data = json.load(f)
    video_id_list = sampled_id_data["sampled_id"]

num_vid_each_user = 10

print("len of video_id_list ", len(video_id_list))

videos_all = [f"{v_id}.mp4" for v_id in video_id_list]

# ======= preparing text prompts ========
text_prompts_en_all = []
text_prompts_zh_all = []
with open(text_en_path, "r", encoding="utf-8") as f:
    for line in f:
        text_prompts_en_all.append(json.loads(line))
with open(text_zh_path, "r", encoding="utf-8") as f:
    for line in f:
        text_prompts_zh_all.append(json.loads(line))

# ======== textual static contents ========
with open(f"./templates/html_text_en/start.txt", "r", encoding="utf-8") as file:
    before_start = file.read()
with open(f"./templates/html_text_zh/start_zh.txt", "r", encoding="utf-8") as file:
    before_start_zh = file.read()

subscore_def_en_list = []
subscore_files = ["question_type.txt", "image.txt", "distractor.txt"]
for fname in subscore_files:
    with open(f"./templates/html_text_en/{fname}", "r", encoding="utf-8") as file:
        content = file.read()
    subscore_def_en_list.append(content)

subscore_def_zh_list = []
subscore_zh_files = [
    "visual_zh.txt",
    "temporal_zh.txt",
    "dynamic_zh.txt",
    "align_zh.txt",
    "factual_zh.txt",
]
for fname in subscore_zh_files:
    with open(f"./templates/html_text_zh/{fname}", "r", encoding="utf-8") as file:
        content = file.read()
    subscore_def_zh_list.append(content)

# ======== user info ========
current_user_dict = {}
with open(user_info_path, "r", encoding="utf-8") as f:
    user_data = json.load(f)
users = list(user_data.keys())
print("users ", users)

with open(user_question_type_info_path, "r", encoding="utf-8") as f:
    user_question_type_data = json.load(f)

s_idx_user_mapping = {}
for user in users:
    curr_user_dict = user_data.get(user)
    s_idx = curr_user_dict.get("s_idx", 0)
    s_idx_user_mapping[f"{s_idx}"] = curr_user_dict.get("username", user)

# ========= validation info ========
annotators = users
answers_all = []
VALIDATE_USER_NAME = "video_admin"
ALLOWED_EXTENSIONS = {
    "png", "jpg", "jpeg", "gif", "webp", "bmp", "tiff", "tif", "heic", "heif", 
    "svg", "psd", "eps", "ai", "pdf", "raw", "cr2", "nef", "arw", "orf", "raf", 
    "dng", "ico", "xcf", "dds", "tga", "avif", "exr", "pcx", "pict", "pic"
}


# ======== user login part ========
class User(UserMixin):
    def __init__(self, id):
        print("user init")
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        print("load user ", user_id)
        return User(user_id)
    else:
        print("user_id not in users_list")
    return None


# ======== webpage_v2 contents ========
@app.route(f"{subpath}", methods=["GET"])
def start():
    return redirect(url_for("welcome"))


@app.route(f"{subpath}welcome", methods=["GET", "POST"])
def welcome():
    session["current_idx"] = 0
    # session["pre_anno_answers"]={}
    session["admin"] = None
    session["s_idx_val"] = 0
    session["e_idx_val"] = len(video_id_list) - 1

    html_file = "welcome.html"
    subscore_def = subscore_def_en_list
    before_start_anno = before_start

    language = request.form.get("language", "en")
    session["language"] = language
    print("welcome language", language)
    if language == "zh":
        session["language"] = "zh"
        html_file = "zh/welcome_zh.html"
        subscore_def = subscore_def_zh_list
        before_start_anno = before_start_zh

    # before_start_anno = markdown.markdown(before_start_anno)
    return render_template(html_file, before_start_anno=before_start_anno)


@app.route(f"{subpath}login_method_1", methods=["POST"])
def login_method_1():
    username = request.form["username"]
    ans_path = f""
    if username in users:
        print("user ", username)
        curr_user_dict = user_data.get(username)
        ans_path = f"{res_dir}/ans_{username}.jsonl"
    else:
        return redirect(url_for("welcome"))

    user = User(username)
    login_user(user)

    curr_user_dict = user_data.get(username)
    session["username"] = curr_user_dict.get("username", username)
    session["s_idx"] = curr_user_dict.get("s_idx", 0)
    session["e_idx"] = curr_user_dict.get("e_idx", len(video_id_list) - 1)
    session["current_idx"] = curr_user_dict.get("current_idx", 0)
    session["video_question_idx"] = 0  # 初始化当前标注索引
    session["image_root"] = f"./upload_images/{username}"
    return redirect(url_for("display"))


@app.route(f"{subpath}login_method_2", methods=["POST"])
def login_method_2():
    username = request.form["username"]
    ans_path = f""
    if username in users:
        print("user ", username)
        curr_user_dict = user_question_type_data.get(username)
        ans_path = f"{res_dir}/ans_{username}.jsonl"
    else:
        return redirect(url_for("welcome"))

    user = User(username)
    login_user(user)

    curr_user_dict = user_question_type_data.get(username)
    session["username"] = curr_user_dict.get("username", username)
    session["s_idx"] = curr_user_dict.get("s_idx", 0)
    session["e_idx"] = curr_user_dict.get("e_idx", len(video_id_list) - 1)
    session["current_idx"] = curr_user_dict.get("current_idx", 0)
    session["video_question_idx"] = 0  # 初始化当前标注索引
    session["image_root"] = f"./upload_images/{username}"
    return redirect(url_for("display_type"))


def load_questions_type(question_type_file, vid_name):
    type_data_list = []
    if os.path.exists(question_type_file):
        with open(question_type_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    type_data_list.append(d)
                except json.JSONDecodeError:
                    continue
    current_question_types = {}
    for type_data in type_data_list:
        if vid_name in type_data.keys():
            current_question_types = type_data[vid_name]
    return current_question_types


def load_annotations(annotation_file, vid_name):
    annotations = []
    if not os.path.exists(annotation_file):
        return annotations
    with open(annotation_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                video_annotations = json.loads(line)
                if vid_name in video_annotations.keys():
                    annotations = video_annotations[vid_name]
                    break
            except json.JSONDecodeError:
                continue
    if not annotations:
        annotations = [
            {
                "data_id": 0,
                "image_name": "",
                "question": "",
                "question_type": "",
                "granularity": "",
                "answer": "",
                "answer_location": "",
                "distractors": [""] * 9,
            }
        ]
    return annotations


@app.route(f"{subpath}annotating", methods=["GET", "POST"])
def display():
    s_idx = session.get("s_idx", 0)
    e_idx = session.get("e_idx", len(video_id_list) - 1)
    videos_curr_user = videos_all[s_idx : e_idx + 1]
    text_prompts_en = text_prompts_en_all[s_idx : e_idx + 1]
    text_prompts_zh = text_prompts_zh_all[s_idx : e_idx + 1]
    username = session.get("username")
    if not username:
        flash("请先登录。")
        return redirect(url_for("welcome"))
    ans_file = f"{res_dir}/ans_{username}.jsonl"
    q_file = f"{res_dir}/q_{username}.jsonl"
    current_video_idx = int(session.get("current_idx", 0))
    video_question_idx = int(session.get("video_question_idx", 0))
    print("curr_video_idx in display ", current_video_idx)
    print("video_question_idx in display ", video_question_idx)

    slice_start_idx = 0
    slice_end_idx = len(videos_curr_user) - 1
    if current_video_idx <= slice_end_idx:
        vid_name = videos_curr_user[current_video_idx].split(".")[0]
        print("video name in display ", f"{vid_name}.mp4")

        video = f"{local_video_dir}/{videos_curr_user[current_video_idx]}"
        annotations = load_annotations(ans_file, vid_name)  # 加载所有标注
        print("annotations loaded: ", annotations)
        if not annotations:
            annotations = [
                {
                    "data_id": 0,
                    "image_name": "",
                    "question": "",
                    "question_type": "",
                    "granularity": "",
                    "answer": "",
                    "answer_location": "",
                    "distractors": [""] * 9,
                }
            ]
        # 确保 video_question_idx 有效
        if video_question_idx >= len(annotations):
            video_question_idx = len(annotations) - 1
            session["video_question_idx"] = video_question_idx
        current_annotation = annotations[video_question_idx]
        current_question_types = load_questions_type(q_file, vid_name)

        html_file = "display.html"
        subscore_def = subscore_def_en_list
        before_start_anno = before_start
        prompt = text_prompts_en[current_video_idx].get("text", "")
        if current_annotation["image_name"] != '':
            current_annotation["image_name"] = os.path.join(session["image_root"], current_annotation["image_name"])
            current_annotation["image_name"] = os.path.normpath(current_annotation["image_name"])
            image_name = current_annotation["image_name"]
            print(f"image_name is:{image_name}")


        return render_template(
            html_file,
            before_start_anno=before_start_anno,
            subscore_def=subscore_def,
            start_index=slice_start_idx,
            end_index=slice_end_idx,
            current_idx=current_video_idx,
            vid_name=vid_name,
            video=video,
            text_prompt=prompt,
            annotation=current_annotation,
            video_question_idx=video_question_idx,
            selected_question_types=current_question_types,
            annotations=annotations,  # 传递所有标注
            title_template=title_template_data,
            distractors_template=distractors_template_data,
            _is_val=0,
        )  # 传递 end_index 给模板
    else:
        current_video_idx = 0
        session["current_idx"] = current_video_idx
        session["video_question_idx"] = 0
        user_data[username]["current_idx"] = session["current_idx"]
        user_data[username]["video_question_idx"] = session["video_question_idx"]
        with open(user_info_path, "w", encoding="utf-8") as file:
            json.dump(user_data, file, indent=4, ensure_ascii=False)

        print("curr_video_idx in display ", current_video_idx)
        return redirect(url_for("display"))


@app.route(f"{subpath}annotating_type", methods=["GET", "POST"])
def display_type():
    s_idx = session.get("s_idx", 0)
    e_idx = session.get("e_idx", len(video_id_list) - 1)
    videos_curr_user = videos_all[s_idx : e_idx + 1]
    text_prompts_en = text_prompts_en_all[s_idx : e_idx + 1]
    text_prompts_zh = text_prompts_zh_all[s_idx : e_idx + 1]
    username = session.get("username")
    if not username:
        flash("请先登录。")
        return redirect(url_for("welcome"))
    question_type_file = f"{res_dir}/q_{username}.jsonl"
    current_video_idx = int(session.get("current_idx", 0))
    video_question_idx = int(session.get("video_question_idx", 0))
    print("curr_video_idx in display_type ", current_video_idx)
    print("video_question_idx in display_type ", video_question_idx)

    slice_start_idx = 0
    slice_end_idx = len(videos_curr_user) - 1
    if current_video_idx <= slice_end_idx:
        vid_name = videos_curr_user[current_video_idx].split(".")[0]
        print("video name in display_type ", f"{vid_name}.mp4")

        video = f"{local_video_dir}/{videos_curr_user[current_video_idx]}"
        print(video)
        answer_data_dict = {}
        if os.path.exists(question_type_file):
            with open(question_type_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        answer_data_dict.update(d)
                    except json.JSONDecodeError:
                        continue

        answered_vid_list = list(answer_data_dict.keys())

        current_answers = []
        if vid_name in answered_vid_list:
            current_answers = answer_data_dict[vid_name]

        # print("answered_vid_list",answered_vid_list)
        print("current_answers (list) ", current_answers)

        html_file = "display_type.html"
        subscore_def = subscore_def_en_list
        before_start_anno = before_start
        prompt = text_prompts_en[current_video_idx].get("text", "")
        language = session.get("language", "en")
        print("language in display_type ", language)

        return render_template(
            html_file,
            before_start_anno=before_start_anno,
            subscore_def=subscore_def,
            start_index=slice_start_idx,
            end_index=slice_end_idx,
            current_idx=current_video_idx,
            vid_name=vid_name,
            video=video,
            text_prompt=prompt,
            answered_vid_list=answered_vid_list,
            selected_question_types=current_answers,
            _is_val=0,
        )  # 传递 end_index 给模板

    else:
        current_video_idx = 0
        session["current_idx"] = current_video_idx
        session["video_question_idx"] = 0
        user_question_type_data[username]["current_idx"] = session["current_idx"]
        user_question_type_data[username]["video_question_idx"] = session[
            "video_question_idx"
        ]
        with open(user_info_path, "w", encoding="utf-8") as file:
            json.dump(user_question_type_data, file, indent=4, ensure_ascii=False)

        print("curr_video_idx in display_type ", current_video_idx)
        return redirect(url_for("display_type"))


@app.route(f"{subpath}navigate_main", methods=["POST"])
def navigate_main():
    s_idx = session.get("s_idx", 0)
    e_idx = session.get("e_idx", len(video_id_list) - 1)
    slice_end_idx = e_idx - s_idx
    direction = request.form.get("direction", "")
    current_video_idx = int(request.form.get("current_idx", 0))
    source_page = request.form.get("source_page")
    if source_page == "display_type":
        video_question_idx = 0
        video_question_number = 1
        move_idx(
            direction,
            slice_end_idx,
            current_video_idx,
            video_question_idx,
            video_question_number,
        )
        return redirect(url_for("display_type"))

    video_question_idx = int(request.form.get("video_question_idx", 0))
    video_question_number = int(request.form.get("video_question_number", 0))
    move_idx(
        direction,
        slice_end_idx,
        current_video_idx,
        video_question_idx,
        video_question_number,
    )
    return redirect(url_for("display"))


def move_idx(
    direction,
    slice_end_idx,
    current_video_idx,
    video_question_idx,
    video_question_number,
):
    # 修改为在当前视频的标注之间导航
    if direction == "last":
        if video_question_idx > 0:
            video_question_idx -= 1
        else:
            # 如果当前是第一个标注，跳转到前一个视频的最后一个标注
            if current_video_idx > 0:
                current_video_idx -= 1
                annotations = load_annotations(
                    f"{res_dir}/ans_{session.get('username')}.jsonl",
                    videos_all[current_video_idx].split(".")[0],
                )
                video_question_number = len(annotations)
                video_question_idx = video_question_number - 1
            else:
                # 已是第一个视频的第一个标注，循环到最后一个视频的最后一个标注
                current_video_idx = slice_end_idx
                annotations = load_annotations(
                    f"{res_dir}/ans_{session.get('username')}.jsonl",
                    videos_all[current_video_idx].split(".")[0],
                )
                video_question_number = len(annotations)
                video_question_idx = video_question_number - 1
    elif direction == "next":
        if video_question_idx < video_question_number - 1:
            video_question_idx += 1
        else:
            # 如果当前是最后一个标注，跳转到下一个视频的第一个标注
            if current_video_idx < slice_end_idx:
                current_video_idx += 1
                video_question_idx = 0
            else:
                # 已是最后一个视频的最后一个标注，循环到第一个视频的第一个标注
                current_video_idx = 0
                video_question_idx = 0

    session["current_idx"] = current_video_idx
    session["video_question_idx"] = video_question_idx
    print("current_idx after navigation ", session.get("current_idx", 0))
    print(
        "video_question_number after navigation ",
        session.get("video_question_number", 1),
    )
    print("video_question_idx after navigation ", session.get("video_question_idx", 0))

    print("navigation of display")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def submit_success(
    username,
    current_video_idx,
    video_question_idx,
    user_data,
    user_info_path,
    video_question_number,
):
    if video_question_idx + 1 >= video_question_number:
        session["current_idx"] = current_video_idx + 1
        session["video_question_idx"] = 0
        session.modified = True
    else:
        session["video_question_idx"] = video_question_idx + 1

    print("idx after submission ", session.get("current_idx", 0))
    print("video_question_idx after submission ", session.get("video_question_idx", 0))

    # 更新用户数据
    if username not in user_data:
        user_data[username] = {}

    user_data[username]["current_idx"] = session["current_idx"]
    user_data[username]["video_question_idx"] = session["video_question_idx"]

    with open(user_info_path, "w", encoding="utf-8") as file:
        json.dump(user_data, file, indent=4, ensure_ascii=False)
    print("*" * 100)
    flash("提交成功！")
    print("*" * 100)


def update_annotation_file(ans_file, vid_name, annotations):
    # 保存回 ans_file
    annotation_dict = {}
    if os.path.exists(ans_file):
        with open(ans_file, "r", encoding="utf-8") as f:
            has_flag = 0
            for line in f:
                try:
                    annotation = json.loads(line)
                    annotation_dict.update(annotation)
                except json.JSONDecodeError:
                    continue

    annotation_dict[vid_name] = annotations
    # 写回 ans_file
    os.makedirs(os.path.dirname(ans_file), exist_ok=True)
    with open(ans_file, "w", encoding="utf-8") as f:
        for vid_name, datas in annotation_dict.items():
            json.dump({vid_name: datas}, f, ensure_ascii=False)
            f.write("\n")


def adjust_image_filenames(vid_name, upload_folder, annotations, operation, affected_idx):
    """
    调整图像文件的命名以保持一致性。

    参数：
    - vid_name (str): 视频名称。
    - upload_folder (str): 图像上传文件夹的路径。
    - annotations (list): 标注列表，每个标注包含 'image_name'。
    - operation (str): 操作类型，'copy' 或 'delete'。
    - affected_idx (int): 受影响的索引位置（复制时为插入位置，删除时为删除位置）。
    """
    if operation not in {"copy", "delete"}:
        raise ValueError("操作类型必须是 'copy' 或 'delete'。")

    # 确定处理顺序
    if operation == "copy":
        # 复制时，先处理较大的索引，以避免重命名冲突
        sorted_annotations = sorted(
            [(i, ann) for i, ann in enumerate(annotations) if ann.get("image_name") and ann["image_name"] != "no_image"],
            key=lambda x: x[0],
            reverse=True
        )
        # 从 affected_idx 开始，所有索引 >= affected_idx 需要加一
        for i, ann in sorted_annotations:
            if i >= affected_idx:
                old_image_name = ann["image_name"]
                filename_parts = old_image_name.split('_', 2)
                if len(filename_parts) == 3 and filename_parts[0] == vid_name:
                    _, idx_str, original_filename = filename_parts
                    try:
                        idx = int(idx_str)
                        new_idx = idx + 1
                        new_image_name = f"{vid_name}_{new_idx}_{original_filename}"
                        print(f"new_image_path is {new_image_name}, old_image_paht is {old_image_name}")
                        old_image_name = os.path.join(upload_folder, old_image_name)
                        new_image_path = os.path.join(upload_folder, new_image_name)
                        if os.path.exists(old_image_name):
                            if i == affected_idx:
                                shutil.copy(old_image_name, new_image_path)
                                ann["image_name"] = new_image_name
                                continue
                            shutil.move(old_image_name, new_image_path)
                            ann["image_name"] = new_image_name
                    except ValueError:
                        # 如果索引部分无法转换为整数，跳过重命名
                        continue

    elif operation == "delete":
        # 删除时，先处理较小的索引，以避免重命名冲突
        sorted_annotations = sorted(
            [(i, ann) for i, ann in enumerate(annotations) if ann.get("image_name") and ann["image_name"] != "no_image"],
            key=lambda x: x[0]
        )

        # 从 affected_idx 开始，所有索引 > affected_idx 需要减一
        for i, ann in sorted_annotations:
            if i >= affected_idx:
                old_image_name = ann["image_name"]
                filename_parts = old_image_name.split('_', 2)
                
                if len(filename_parts) == 3 and filename_parts[0] == vid_name:
                    _, idx_str, original_filename = filename_parts
                    idx = int(idx_str)
                    new_idx = idx - 1
                    new_image_name = f"{vid_name}_{new_idx}_{original_filename}"

                    # 获取图片的绝对路径
                    old_image_path = os.path.join(upload_folder, old_image_name)
                    new_image_path = os.path.join(upload_folder, new_image_name)

                    # 如果图片文件存在，删除或重命名
                    if os.path.exists(old_image_path):
                        if i == affected_idx:
                            # 删除当前图片文件
                            os.remove(old_image_path)
                            continue  # 删除完毕后跳过这个元素

                        # 移动图片文件，并更新路径
                        shutil.move(old_image_path, new_image_path)
                        ann["image_name"] = new_image_name



@app.route("/submit", methods=["POST"])
def submit():
    username = session.get("username")
    if not username:
        # 处理未登录或未设置用户名的情况
        flash("请先登录。")
        return redirect(url_for("welcome"))

    # 配置上传文件夹和允许的扩展名
    UPLOAD_FOLDER = f"./videos/upload_images/{username}"
    # 检查是否存在，不存在则创建
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Folder '{UPLOAD_FOLDER}' created successfully.")
    else:
        print(f"Folder '{UPLOAD_FOLDER}' already exists.")
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    ans_file = f"{res_dir}/ans_{username}.jsonl"
    question_type_file = f"{res_dir}/q_{username}.jsonl"

    action = request.form.get("action", "")
    s_idx = session.get("s_idx", 0)
    e_idx = session.get("e_idx", len(video_id_list) - 1)
    slice_end_idx = e_idx - s_idx
    source_page = request.form.get("source_page")

    current_video_idx = int(request.form.get("current_idx", 0))
    video_question_idx = int(request.form.get("video_question_idx", 0))
    video_question_number = int(request.form.get("video_question_number", 0))
    vid_name = request.form.get("video", "").split("/")[-1].split(".")[0]

    if action == "navigate":
        # 处理跳转到指定索引，不进行metadata的完备性检查
        try:
            next_idx = int(request.form.get("next_idx", 1)) - 1
            # 确保 next_idx 在视频范围内
            if next_idx < 0 or next_idx > slice_end_idx:
                flash("跳转的索引超出范围。")
                return redirect(url_for("display"))
            session["current_idx"] = next_idx
            session["video_question_idx"] = 0  # 切换视频时重置标注索引
            session.modified = True
            flash(f"已跳转到索引 {next_idx + 1}。")
            if source_page == "display_type":
                return redirect(url_for("display_type"))
            return redirect(url_for("display"))
        except ValueError:
            flash("无效的索引值。")
            if source_page == "display_type":
                return redirect(url_for("display_type"))
            return redirect(url_for("display"))

    elif action == "copy":
        # 处理复制操作
        annotations = load_annotations(ans_file, vid_name)
        if not annotations:
            annotations = [
                {
                    "data_id": 0,
                    "image_name": "",
                    "question": "",
                    "question_type": "",
                    "granularity": "",
                    "answer": "",
                    "answer_location": "",
                    "distractors": [""] * 9,
                }
            ]
        current_annotation = annotations[video_question_idx]

        # 创建复制的标注
        copied_annotation = current_annotation.copy()
        copied_annotation["data_id"] = video_question_idx + 1


        annotations.insert(video_question_idx + 1, copied_annotation)

        # 更新后续标注的 data_id
        for i in range(video_question_idx + 2, len(annotations)):
            annotations[i]["data_id"] = annotations[i]["data_id"] + 1
        
        # 调整图像文件名，传递正确的 affected_idx
        adjust_image_filenames(vid_name, app.config["UPLOAD_FOLDER"], annotations, 'copy', video_question_idx + 1)
        print(f"annotations after copy is {annotations}")

        video_question_number = len(annotations)

        update_annotation_file(ans_file, vid_name, annotations)

        flash("已复制当前条目。")

        direction = "next"
        session["video_question_number"] = video_question_number
        move_idx(
            direction,
            slice_end_idx,
            current_video_idx,
            video_question_idx,
            video_question_number,
        )
        return redirect(url_for("display"))

    elif action == "delete":
        # 处理删除操作
        annotations = load_annotations(ans_file, vid_name)

        # if len(annotations) <= 1:
        #     flash("每个视频至少保留一条数据，无法删除。")
        #     return redirect(url_for("display"))

        adjust_image_filenames(vid_name, app.config["UPLOAD_FOLDER"], annotations, 'delete', video_question_idx)

        removed_annotation = annotations.pop(video_question_idx)
        # 判断video_question_idx是否不是最后一个元素
        if video_question_idx < len(annotations):
            # 如果是中间元素，更新后面所有元素的data_id
            for i in range(video_question_idx, len(annotations)):
                annotations[i]["data_id"] = annotations[i]["data_id"] - 1
        print(f"annotations after delete is {annotations}")
        
        video_question_number = len(annotations)
        # 调整 video_question_idx 如果需要
        if video_question_idx >= video_question_number:
            video_question_idx = video_question_number - 1
            session["video_question_idx"] = video_question_idx

        update_annotation_file(ans_file, vid_name, annotations)
        flash("已删除当前条目。")
        return redirect(url_for("display"))

    elif action == "submit":
        if source_page == "display_type":
            # 处理 question type 的提交
            current_video_idx = int(request.form.get("current_idx", 0))
            video_question_idx = int(request.form.get("video_question_idx", 0))
            question_type = request.form.getlist("question_type")
            vid_name = os.path.splitext(
                os.path.basename(request.form.get("video", ""))
            )[0]

            # 加载现有的 question_type 数据
            answer_data_dict = {}
            if os.path.exists(question_type_file):
                with open(question_type_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            d = json.loads(line)
                            answer_data_dict.update(d)
                        except json.JSONDecodeError:
                            continue

            # 更新当前视频的 question_type
            answer_data_dict[vid_name] = question_type

            # 保存回 question_type_file
            with open(question_type_file, "w", encoding="utf-8") as f:
                for vid, types in answer_data_dict.items():
                    json_line = json.dumps({vid: types}, ensure_ascii=False)
                    f.write(json_line + "\n")

            # 更新 current_idx 和 video_question_idx
            session["current_idx"] = current_video_idx + 1
            session["video_question_idx"] = 0
            session.modified = True

            flash("Question Type 已成功更新。")
            return redirect(url_for("display_type"))

        # 处理标注数据的提交
        current_video_idx = int(request.form.get("current_idx", 0))
        video_question_idx = int(request.form.get("video_question_idx", 0))
        video_question_number = int(request.form.get("video_question_number", 0))
        vid_name = request.form.get("video", "").split("/")[-1].split(".")[0]
        text = request.form.get("question", "")


        # 加载现有的标注
        annotations = load_annotations(ans_file, vid_name)
        if not annotations:
            annotations = [
                {
                    "data_id": 0,
                    "image_name": "",
                    "question": "",
                    "question_type": "",
                    "granularity": "",
                    "answer": "",
                    "answer_location": "",
                    "distractors": [""] * 9,
                }
            ]

        image = request.files.get("image")
        image_filename = None
        unique_filename = "no_image"  # 默认值

        if image and image.filename != "":
            if allowed_file(image.filename):
                filename = secure_filename(image.filename)
                unique_filename = f"{vid_name}_{video_question_idx}_{filename}"
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
                image.save(image_path)
                image_filename = unique_filename
                print(f"image has been saved in {image_path}")
            else:
                # 上传了文件但不符合扩展名要求
                flash("不支持的文件类型。")
                return redirect(url_for("display"))

        if not image_filename:
            current_annotation = annotations[video_question_idx]
            image_filename = current_annotation["image_name"]
        # 构建答案字典
        answer_dict = {
            "data_id": video_question_idx,  # 使用当前索引作为 data_id
            "image_name": image_filename if image_filename else "",
            "question": text,
            "question_type": request.form.get("question_type", ""),
            "granularity": request.form.get("granularity", ""),
            "answer": request.form.get("answer", ""),
            "answer_location": request.form.get("answer_location", ""),
            "distractors": [
                request.form.get(f"distractor{i}", "") for i in range(1, 10)
            ],
        }

        # 更新当前标注
        if len(annotations) > video_question_idx:
            annotations[video_question_idx] = answer_dict
        else:
            annotations.append(answer_dict)

        update_annotation_file(ans_file, vid_name, annotations)

        # 更新 video_question_idx 如果需要
        submit_success(
            username,
            current_video_idx,
            video_question_idx,
            user_data,
            user_info_path,
            video_question_number,
        )
        return redirect(url_for("display"))

    else:
        flash("未知的操作。")
        return redirect(url_for("display"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT_NUM, debug=False)
