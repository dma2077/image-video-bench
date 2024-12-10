from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import timedelta
import json
import datetime
import os
from werkzeug.utils import secure_filename
import uuid
import markdown

# ======== static and global variables ========
#static_root_path = "/map-vepfs/dehua/data/image-video-bench/image-video-bench/videos"
static_root_path = "E:/Code/image-video-bench/videos"


app = Flask(__name__, static_folder=static_root_path)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=100)
PORT_NUM = 22002
subpath = "/image_video_bench/"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


local_video_dir = "./examples/youtube_0518"
res_dir = "./res/res_current"
get_image_root = "./upload_images"
text_files_dir = "text_files"
text_en_path = f"./{text_files_dir}/text_en_display.jsonl"
text_zh_path = f"./{text_files_dir}/text_zh_display.jsonl"
user_info_path = f"./{text_files_dir}/user_info.json"
user_question_type_info_path = f"./{text_files_dir}/user_question_type_info.json"

reported_problem_log = f"./{text_files_dir}/problem_reported.json"
sampled_id_file = f"./{text_files_dir}/sampled_id_youtube_0518.json"

# 配置上传文件夹和允许的扩展名
UPLOAD_FOLDER = './videos/upload_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ======== preparing video-ids and videos  =========
video_id_list = []
videos = []

with open(sampled_id_file, 'r', encoding='utf-8') as f:
    sampled_id_data = json.load(f)
    video_id_list = sampled_id_data["sampled_id"]

num_vid_each_user = 10

print("len of video_id_list ", len(video_id_list))

videos_all = [f"{v_id}.mp4" for v_id in video_id_list]


# ======= preparing text prompts ======== 
text_prompts_en_all = []
text_prompts_zh_all = []
with open(text_en_path, "r", encoding='utf-8') as f:
    for line in f:
        text_prompts_en_all.append(json.loads(line))
with open(text_zh_path, "r", encoding='utf-8') as f:
    for line in f:
        text_prompts_zh_all.append(json.loads(line))


# ======== textual static contents ========
with open(f'./templates/html_text_en/start.txt', 'r', encoding='utf-8') as file:
    before_start = file.read()
with open(f'./templates/html_text_zh/start_zh.txt', 'r', encoding='utf-8') as file:
    before_start_zh = file.read()

subscore_def_en_list = []
subscore_files = ["question_type.txt", "image.txt", "distractor.txt"]
for fname in subscore_files:
    with open(f'./templates/html_text_en/{fname}', 'r', encoding='utf-8') as file:
        content = file.read()
    subscore_def_en_list.append(content)   

subscore_def_zh_list = []
subscore_zh_files = ["visual_zh.txt", "temporal_zh.txt", "dynamic_zh.txt", "align_zh.txt", "factual_zh.txt"]
for fname in subscore_zh_files:
    with open(f'./templates/html_text_zh/{fname}', 'r', encoding='utf-8') as file:
        content = file.read()
    subscore_def_zh_list.append(content)


# ======== user info ========
current_user_dict = {}
with open(user_info_path, 'r', encoding='utf-8') as f:
    user_data = json.load(f)
users = list(user_data.keys())
print("users ", users)

with open(user_question_type_info_path, 'r', encoding='utf-8') as f:
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
@app.route(f'{subpath}', methods=['GET'])
def start():
    return redirect(url_for('welcome'))


@app.route(f'{subpath}welcome', methods=['GET', 'POST'])
def welcome():
    session['current_idx'] = 0
    # session["pre_anno_answers"]={}
    session['admin'] = None
    session['s_idx_val'] = 0
    session['e_idx_val'] = len(video_id_list) - 1

    html_file = "welcome.html"
    subscore_def = subscore_def_en_list
    before_start_anno = before_start

    language = request.form.get('language', "en")
    session["language"] = language
    print("welcome language", language)
    if language == "zh":
        session["language"] = "zh"
        html_file = "zh/welcome_zh.html"
        subscore_def = subscore_def_zh_list
        before_start_anno = before_start_zh

    # before_start_anno = markdown.markdown(before_start_anno)
    return render_template(html_file,
                           before_start_anno=before_start_anno)


@app.route(f'{subpath}login_method_1', methods=['POST'])
def login_method_1():
    username = request.form['username']
    ans_path = f""
    if username in users:
        print("user ", username)
        curr_user_dict = user_data.get(username)
        ans_path = f"{res_dir}/ans_{username}.jsonl"
    else:
        return redirect(url_for('welcome'))
        
    user = User(username)
    login_user(user)

    curr_user_dict = user_data.get(username)
    session['username'] = curr_user_dict.get("username", username)
    session['s_idx'] = curr_user_dict.get('s_idx', 0)
    session['e_idx'] = curr_user_dict.get('e_idx', len(video_id_list)-1)
    session['current_idx'] = curr_user_dict.get('current_idx', 0)
    return redirect(url_for('display'))

@app.route(f'{subpath}login_method_2', methods=['POST'])
def login_method_2():
    username = request.form['username']
    ans_path = f""
    if username in users:
        print("user ", username)
        curr_user_dict = user_question_type_data.get(username)
        ans_path = f"{res_dir}/ans_{username}.jsonl"
    else:
        return redirect(url_for('welcome'))
        
    user = User(username)
    login_user(user)

    curr_user_dict = user_question_type_data.get(username)
    session['username'] = curr_user_dict.get("username", username)
    session['s_idx'] = curr_user_dict.get('s_idx', 0)
    session['e_idx'] = curr_user_dict.get('e_idx', len(video_id_list)-1)
    session['current_idx'] = curr_user_dict.get('current_idx', 0)
    return redirect(url_for('display_type'))


def load_questions_type(question_type_file, vid_name):
    type_data_list = []
    if os.path.exists(question_type_file):
        with open(question_type_file, 'r', encoding='utf-8') as f:
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

def load_annotation(annotation_file, vid_name):
    if not os.path.exists(annotation_file):
        return {
            'image': '',
            'question': '',
            'question_type': '',
            'granularity': '',
            'answer': '',
            'answer_location': '',
            'distractors': [''] * 9
        }

    with open(annotation_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                annotation = json.loads(line)
                if annotation.get('video_name') == vid_name:
                    return {
                        'image': get_image_root + "/" + annotation.get('image_name', ''),
                        'question': annotation.get('question', ''),
                        'question_type': annotation.get('question_type', ''),
                        'granularity': annotation.get('granularity', ''),
                        'answer': annotation.get('answer', ''),
                        'answer_location': annotation.get('answer_location', ''),
                        'distractors': annotation.get('distractors', [''] * 9)
                    }
            except json.JSONDecodeError:
                continue

    return {
        'image': '',
        'question': '',
        'question_type': '',
        'granularity': '',
        'answer': '',
        'answer_location': '',
        'distractors': [''] * 9
    }



@app.route(f'{subpath}annotating', methods=['GET', 'POST'])
def display():
    s_idx = session.get("s_idx", 0)
    e_idx = session.get("e_idx", len(video_id_list)-1)
    videos_curr_user = videos_all[s_idx:e_idx + 1]
    text_prompts_en = text_prompts_en_all[s_idx:e_idx + 1]
    text_prompts_zh = text_prompts_zh_all[s_idx:e_idx + 1]
    username = session.get("username")
    if not username:
        flash("请先登录。")
        return redirect(url_for('welcome'))
    ans_file = f"{res_dir}/ans_{username}.jsonl"
    q_file = f"{res_dir}/q_{username}.jsonl"
    current_idx = int(session.get("current_idx", 0))
    print("curr_idx in display ", current_idx)
    
    slice_start_idx = 0
    slice_end_idx = len(videos_curr_user) - 1
    if current_idx <= slice_end_idx:
        vid_name = videos_curr_user[current_idx].split(".")[0]
        print("video name in display ", f"{vid_name}.mp4")
        
        video = f"{local_video_dir}/{videos_curr_user[current_idx]}"
        current_annotation = load_annotation(ans_file, vid_name)
        print(current_annotation)
        current_question_types = load_questions_type(q_file, vid_name)
        
        html_file = "display.html"
        subscore_def = subscore_def_en_list
        before_start_anno = before_start
        prompt = text_prompts_en[current_idx].get("text", "")

        return render_template(html_file, 
            before_start_anno=before_start_anno,
            subscore_def=subscore_def,
            start_index=slice_start_idx,
            end_index=slice_end_idx,
            current_idx=current_idx,
            vid_name=vid_name,
            video=video,
            text_prompt=prompt,
            annotation=current_annotation,
            selected_question_types=current_question_types,
            _is_val=0)  # 传递 end_index 给模板

    else:
        current_idx = 0
        session["current_idx"] = current_idx
        user_data[username]['current_idx'] = session['current_idx']
        with open(user_info_path, "w", encoding='utf-8') as file:
            json.dump(user_data, file, indent=4, ensure_ascii=False)

        print("curr_idx in display ", current_idx)
        return redirect(url_for('display'))

@app.route(f'{subpath}annotating_type', methods=['GET', 'POST'])
def display_type():
    s_idx = session.get("s_idx", 0)
    e_idx = session.get("e_idx", len(video_id_list)-1)
    videos_curr_user = videos_all[s_idx:e_idx + 1]
    text_prompts_en = text_prompts_en_all[s_idx:e_idx + 1]
    text_prompts_zh = text_prompts_zh_all[s_idx:e_idx + 1]
    username = session.get("username")
    if not username:
        flash("请先登录。")
        return redirect(url_for('welcome'))
    question_type_file = f"{res_dir}/q_{username}.jsonl"
    current_idx = int(session.get("current_idx", 0))
    print("curr_idx in display ", current_idx)
    
    slice_start_idx = 0
    slice_end_idx = len(videos_curr_user) - 1
    if current_idx <= slice_end_idx:
        vid_name = videos_curr_user[current_idx].split(".")[0]
        print("video name in display ", f"{vid_name}.mp4")
        
        video = f"{local_video_dir}/{videos_curr_user[current_idx]}"
        print(video)
        answer_data_dict = {}
        if os.path.exists(question_type_file):
            with open(question_type_file, 'r', encoding='utf-8') as f:
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
        prompt = text_prompts_en[current_idx].get("text", "")
        language = session.get("language", "en")
        print("language in display ", language)

        return render_template(html_file, 
            before_start_anno=before_start_anno,
            subscore_def=subscore_def,
            start_index=slice_start_idx,
            end_index=slice_end_idx,
            current_idx=current_idx,
            vid_name=vid_name,
            video=video,
            text_prompt=prompt,
            answered_vid_list=answered_vid_list,
            selected_question_types=current_answers,
            _is_val=0)  # 传递 end_index 给模板

    else:
        current_idx = 0
        session["current_idx"] = current_idx
        user_question_type_data[username]['current_idx'] = session['current_idx']
        with open(user_info_path, "w", encoding='utf-8') as file:
            json.dump(user_question_type_data, file, indent=4, ensure_ascii=False)

        print("curr_idx in display ", current_idx)
        return redirect(url_for('display_type'))


@app.route(f'{subpath}navigate_main', methods=['POST'])
def navigate_main():
    s_idx = session.get("s_idx", 0)
    e_idx = session.get("e_idx", len(video_id_list)-1)
    slice_end_idx = e_idx - s_idx
    direction = request.form.get('direction', '')
    current_idx = int(request.form.get('current_idx', 0))
    source_page = request.form.get('source_page')
    print(source_page)
    if direction == 'last':
        if current_idx > 0:
            current_idx -= 1
        else:
            current_idx = slice_end_idx
    elif direction == 'next':
        if current_idx < slice_end_idx:
            current_idx += 1
        else:
            current_idx = 0

    session["current_idx"] = current_idx
    print("idx after navigation ", session.get("current_idx", 0))
    
    print("navigation of display")
    if source_page == "display_type":
        return redirect(url_for("display_type"))
    return redirect(url_for('display'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def submit_success(username, current_idx, user_data, user_info_path, url_name):
    session['current_idx'] = current_idx + 1
    session.modified = True

    print("idx after submission ", session.get("current_idx", 0))

    # 更新用户数据
    if username not in user_data:
        user_data[username] = {}

    user_data[username]['current_idx'] = session['current_idx']

    with open(user_info_path, "w", encoding='utf-8') as file:
        json.dump(user_data, file, indent=4, ensure_ascii=False)
    print("*"*100)
    flash("提交成功！")
    print("*"*100)


@app.route('/submit', methods=['POST'])
def submit():
    username = session.get('username')
    if not username:
        # 处理未登录或未设置用户名的情况
        flash("请先登录。")
        return redirect(url_for('welcome'))

    ans_file = f"{res_dir}/ans_{username}.jsonl"
    question_type_file = f"{res_dir}/q_{username}.jsonl"
    
    
    action = request.form.get('action', '')
    s_idx = session.get('s_idx', 0)
    e_idx = session.get('e_idx', len(video_id_list)-1)
    slice_end_idx = e_idx - s_idx
    source_page = request.form.get('source_page')
    if action == 'navigate':
        # 处理跳转到指定索引，不进行metadata的完备性检查
        try:
            next_idx = int(request.form.get('next_idx', 1)) - 1
            # 确保 next_idx 在有效范围内
            if next_idx < 0 or next_idx > slice_end_idx:
                flash("跳转的索引超出范围。")
                return redirect(url_for('display'))
            session['current_idx'] = next_idx
            session.modified = True
            flash(f"已跳转到索引 {next_idx + 1}。")
            if source_page == "display_type":
                return redirect(url_for("display_type"))
            return redirect(url_for('display'))
        except ValueError:
            flash("无效的索引值。")
            if source_page == "display_type":
                return redirect(url_for("display_type"))
            return redirect(url_for('display'))

    elif action == 'submit':
        if source_page == "display_type":
            current_idx = int(request.form.get('current_idx', 0))
            question_type = request.form.getlist('question_type')
            vid_name = os.path.splitext(os.path.basename(request.form.get('video', '')))[0]
            
            # 加载现有的 question_type 数据
            answer_data_dict = {}
            if os.path.exists(question_type_file):
                with open(question_type_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            d = json.loads(line)
                            answer_data_dict.update(d)
                        except json.JSONDecodeError:
                            continue

            # 更新当前视频的 question_type
            answer_data_dict[vid_name] = question_type

            # 将更新后的数据写回 JSONL 文件（覆盖原文件）
            with open(question_type_file, 'w', encoding='utf-8') as f:
                for vid, types in answer_data_dict.items():
                    json_line = json.dumps({vid: types}, ensure_ascii=False)
                    f.write(json_line + '\n')

            # 更新当前索引
            session['current_idx'] = current_idx + 1
            session.modified = True

            flash("Question Type 已成功更新。")
            return redirect(url_for("display_type"))
        
        # 获取并处理表单数据
        current_idx = int(request.form.get('current_idx', 0))
        vid_name = request.form.get('video', '').split("/")[-1].split(".")[0]
        text = request.form.get('question', '')

        # 处理上传的图片
        image = request.files.get('image')
        image_filename = None
        unique_filename = "no_image"  # 默认值

        if image and image.filename != '':
            if allowed_file(image.filename):
                # 使用安全的文件名
                filename = secure_filename(image.filename)
                # 为了确保唯一性，使用UUID前缀
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                image.save(image_path)
                image_filename = unique_filename
                print(f"image has been saved in {image_path}")
            else:
                # 上传了文件但不符合扩展名要求
                flash("不支持的文件类型。")
                return redirect(url_for('display'))

        # 构建答案字典
        answer_dict = {
            "data_id": current_idx,  # 使用当前索引作为 data_id
            "video_name": vid_name,
            "image_name": image_filename if image_filename else "",
            "question": text,
            "question_type": request.form.get('question_type', ''),
            "granularity": request.form.get('granularity', ''),
            "answer": request.form.get('answer', ''),
            "answer_location": request.form.get('answer_location', ''),
            "distractors": [request.form.get(f'distractor{i}', '') for i in range(1, 10)]
        }
        
        # 保存到答案文件
        with open(ans_file, "a+", encoding='utf-8') as file:
            json.dump(answer_dict, file, ensure_ascii=False)
            file.write('\n')
            
        submit_success(username, current_idx, user_data, user_info_path, 'display')
        return redirect(url_for('display'))

    else:
        flash("未知的操作。")
        return redirect(url_for('display'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT_NUM)
