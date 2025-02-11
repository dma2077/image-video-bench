import os
import json
from collections import Counter

def check_data(data):
    count = 0 
    for question in data:
        if question['image_name'] != '':
            count += 1
    return count


def analyze_data(directory):
    yes_no_counter = Counter()  # 用于统计是/否答案的数量
    number_counter = Counter()  # 用于统计数字答案的数量
    question_type_counter = Counter()  # 用于统计question_type的分布
    total_data_count = 0  # 用于统计总数据条数
    total_dict_count = 0  # 用于统计总字典个数
    video_set = set()
    question_options = {}  # 用于记录每个问题类别对应的所有选项数

    # 遍历目录中的所有jsonl文件
    for filename in os.listdir(directory):
        if filename.endswith(".jsonl"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    data = json.loads(line.strip())
                    key, value = next(iter(data.items()))
                    if check_data(value) > 0:
                        video_set.add(key)
                        total_data_count += 1  # 每读取一行数据，计数器加1
            
                    if isinstance(data, dict) and len(data) == 1:
                        # 提取列表中的每个字典
                        key, value = next(iter(data.items()))
                        if isinstance(value, list):
                            total_dict_count += check_data(value)  # 统计该行中的字典个数
                            for item in value:
                                # 统计“是/否”答案
                                answer = item.get('answer')
                                if answer in ["是", "否"]:
                                    yes_no_counter[answer] += 1
                                elif answer.isdigit():  # 统计数字答案
                                    number_counter[answer] += 1
                                
                                # 统计question_type
                                question_type = item.get('question_type')
                                if question_type:
                                    question_type_counter[question_type] += 1

                                    # 统计每个问题类型的选项数，过滤掉空字符的干扰项
                                    distractors = item.get('distractors', [])
                                    # 过滤掉空字符的干扰项
                                    valid_distractors = [d for d in distractors if d.strip() != '']
                                    k = len(valid_distractors) + 1  # 选项数 = 有效干扰项数 + 1 (正确答案)
                                    if question_type not in question_options:
                                        question_options[question_type] = []
                                    question_options[question_type].append(k)

    # 计算比例并排序
    total_yes_no = sum(yes_no_counter.values())
    yes_no_ratio = sorted(
        {key: count / total_yes_no for key, count in yes_no_counter.items()}.items(),
        key=lambda x: x[1], reverse=True
    ) if total_yes_no > 0 else []

    total_numbers = sum(number_counter.values())
    number_ratio = sorted(
        {key: count / total_numbers for key, count in number_counter.items()}.items(),
        key=lambda x: x[1], reverse=True
    ) if total_numbers > 0 else []

    total_question_types = sum(question_type_counter.values())
    question_type_ratio = sorted(
        {key: count / total_question_types for key, count in question_type_counter.items()}.items(),
        key=lambda x: x[1], reverse=True
    ) if total_question_types > 0 else []

    print(len(video_set))
    # 计算平均字典个数
    avg_dict_per_line = total_dict_count / total_data_count if total_data_count > 0 else 0

    # 计算每个问题类别的随机猜对概率
    random_guess_probabilities = {}
    total_question_type_weight = 0  # 计算总问题类型加权和
    weighted_random_guess = 0  # 用于计算加权后的总随机猜测概率

    for question_type, k_values in question_options.items():
        # 随机猜对的概率 = 1 / k
        avg_k = sum(k_values) / len(k_values) if k_values else 0
        random_guess_probabilities[question_type] = 1 / avg_k if avg_k > 0 else 0
                # 计算问题类别的加权和（频率 * 概率）
        question_type_weight = question_type_counter[question_type] / total_question_types
        weighted_random_guess += question_type_weight * random_guess_probabilities[question_type]
        total_question_type_weight += question_type_weight

    total_random_guess_probability = weighted_random_guess

    return total_data_count, avg_dict_per_line, yes_no_ratio, number_ratio, question_type_ratio, random_guess_probabilities, total_random_guess_probability

# 指定路径
directory_path = "/Users/dehua/code/image-video-bench/res/res_current/"
total_data_count, avg_dict_per_line, yes_no_ratio, number_ratio, question_type_ratio, random_guess_probabilities, total_random_guess_probability = analyze_data(directory_path)

# 输出结果
print(f"Total Number of Data Entries: {total_data_count}")
print(f"Average Number of Dictionaries Per Line: {avg_dict_per_line:.2f}")
print("Yes/No Answer Ratio (Descending):", yes_no_ratio)
print("Number Answer Ratio (Descending):", number_ratio)
print("Question Type Ratio (Descending):", question_type_ratio)
print("Random Guess Probability for Each Question Type:")
for question_type, prob in random_guess_probabilities.items():
    print(f"{question_type}: {prob:.4f}")
print(f"Total Random Guess Probability for All Categories: {total_random_guess_probability:.4f}")