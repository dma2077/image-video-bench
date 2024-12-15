import json
import numpy as np
import pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE
#import matplotlib.pyplot as plt
from tqdm import tqdm
import os

# ----------------------------- #
# 1. 数据加载与预处理
# ----------------------------- #

def load_embeddings(jsonl_path):
    """
    从JSONL文件加载video_id和embedding。

    Args:
        jsonl_path (str): JSONL文件路径。

    Returns:
        video_ids (List[str]): video_id列表。
        embeddings (np.ndarray): 形状为 (N, 1024) 的嵌入向量。
    """
    video_ids = []
    embeddings = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="加载嵌入数据"):
            try:
                data = json.loads(line)
                video_id = data.get('video_id')
                embedding = data.get('embedding')
                if video_id is not None and embedding is not None and len(embedding) == 1024:
                    video_ids.append(video_id)
                    embeddings.append(embedding)
                else:
                    # 跳过不符合条件的数据
                    continue
            except json.JSONDecodeError:
                # 跳过无法解析的行
                continue
    embeddings = np.array(embeddings, dtype=np.float32)
    print(f"加载完成。总数据量: {len(video_ids)} 条")
    return video_ids, embeddings

def load_durations(jsonl_path):
    """
    从JSONL文件加载video_id和duration。

    Args:
        jsonl_path (str): JSONL文件路径。

    Returns:
        durations_dict (Dict[str, float]): video_id到duration（秒）的映射。
    """
    durations_dict = {}
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="加载时长数据"):
            try:
                data = json.loads(line)
                video_id = data.get('video_id')
                duration = data.get('duration', 0)
                if video_id is not None:
                    # 转换duration为float
                    if isinstance(duration, (int, float)):
                        durations_dict[video_id] = float(duration)
                    elif isinstance(duration, str):
                        try:
                            durations_dict[video_id] = float(duration)
                        except ValueError:
                            # 无法转换为数字，跳过
                            continue
                    else:
                        # 不支持的类型，跳过
                        continue
            except json.JSONDecodeError:
                # 跳过无法解析的行
                continue
    print(f"加载完成。总时长数据量: {len(durations_dict)} 条")
    return durations_dict

def merge_data(emb_video_ids, embeddings, dur_dict):
    """
    合并视频嵌入、视频ID和时长数据。

    Args:
        emb_video_ids (List[str]): 嵌入数据中的video_id列表。
        embeddings (np.ndarray): 嵌入向量。
        dur_dict (Dict[str, float]): video_id到duration的映射。

    Returns:
        merged_video_ids (List[str]): 合并后的video_id列表。
        merged_embeddings (np.ndarray): 合并后的嵌入向量。
        merged_durations (List[float]): 合并后的duration列表。
    """
    merged_video_ids = []
    merged_embeddings = []
    merged_durations = []
    for vid, emb in zip(emb_video_ids, embeddings):
        duration = dur_dict.get(vid)
        if duration is not None:
            merged_video_ids.append(vid)
            merged_embeddings.append(emb)
            merged_durations.append(duration)
    merged_embeddings = np.array(merged_embeddings, dtype=np.float32)
    print(f"合并完成。合并后的数据量: {len(merged_video_ids)} 条")
    return merged_video_ids, merged_embeddings, merged_durations

# ----------------------------- #
# 2. 降维（可选）
# ----------------------------- #

def reduce_dimensionality(embeddings, n_components=100, random_state=42):
    """
    使用PCA降维。

    Args:
        embeddings (np.ndarray): 原始嵌入向量。
        n_components (int): 降维后的维度。
        random_state (int): 随机种子。

    Returns:
        reduced_embeddings (np.ndarray): 降维后的嵌入向量。
    """
    pca = PCA(n_components=n_components, random_state=random_state)
    reduced_embeddings = pca.fit_transform(embeddings)
    print(f"PCA降维完成。降维前形状: {embeddings.shape}, 降维后形状: {reduced_embeddings.shape}")
    return reduced_embeddings

# ----------------------------- #
# 3. 聚类
# ----------------------------- #

def perform_clustering(embeddings, num_clusters=10, batch_size=1000, random_state=42):
    """
    使用MiniBatchKMeans进行聚类。

    Args:
        embeddings (np.ndarray): 嵌入向量。
        num_clusters (int): 簇的数量。
        batch_size (int): MiniBatchKMeans的批量大小。
        random_state (int): 随机种子。

    Returns:
        kmeans (MiniBatchKMeans): 训练好的聚类模型。
        labels (np.ndarray): 每个样本的簇标签。
    """
    print(f"开始聚类，簇数量: {num_clusters}")
    kmeans = MiniBatchKMeans(n_clusters=num_clusters, batch_size=batch_size, random_state=random_state, verbose=1, max_iter=1000)
    kmeans.fit(embeddings)
    labels = kmeans.labels_
    print(f"聚类完成。簇标签分布: {np.bincount(labels)}")
    return kmeans, labels

# ----------------------------- #
# 4. 选择代表性样本
# ----------------------------- #

def select_representative_samples(video_ids, embeddings, durations, labels, num_clusters, kmeans_model, 
                                 samples_per_cluster=110, duration_constraints=None):
    """
    从每个簇中选择距离簇中心最近的多个样本，并满足时长比例。

    Args:
        video_ids (List[str]): video_id列表。
        embeddings (np.ndarray): 降维后的嵌入向量。
        durations (List[float]): 视频时长列表（秒）。
        labels (np.ndarray): 簇标签。
        num_clusters (int): 簇的数量。
        kmeans_model (MiniBatchKMeans): 训练好的聚类模型。
        samples_per_cluster (int): 每个簇选择的样本数量。
        duration_constraints (Dict[str, int]): 各时长类别的样本数量。

    Returns:
        representative_video_ids (List[str]): 选择的代表性video_id列表。
    """
    if duration_constraints is None:
        duration_constraints = {
            '5-10': 80,    # 每个簇中选择80个5-10分钟的视频
            '10-30': 20,   # 每个簇中选择20个10-30分钟的视频
            '30+': 10      # 每个簇中选择10个30分钟以上的视频
        }
    
    # 定义时长类别
    def categorize_duration(duration):
        if 300 <= duration <= 600:
            return '5-10'
        elif 600 < duration <= 1800:
            return '10-30'
        elif duration > 1800:
            return '30+'
        else:
            return 'others'
    
    # 为每个样本分配类别
    duration_categories = [categorize_duration(dur) for dur in durations]
    
    representative_video_ids = []
    
    for i in tqdm(range(num_clusters), desc="选择代表性样本"):
        cluster_indices = np.where(labels == i)[0]
        if len(cluster_indices) == 0:
            continue  # 某些簇可能为空
        cluster_embeddings = embeddings[cluster_indices]
        centroid = kmeans_model.cluster_centers_[i]
        # 计算每个样本与质心的距离
        distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
        # 创建DataFrame以便处理
        cluster_df = pd.DataFrame({
            'index': cluster_indices,
            'distance': distances,
            'category': [duration_categories[idx] for idx in cluster_indices]
        })
        
        # 过滤出各类别
        selected_indices = []
        for category, count in duration_constraints.items():
            category_df = cluster_df[cluster_df['category'] == category].sort_values('distance')
            selected = category_df.head(count)['index'].tolist()
            selected_indices.extend(selected)
        
        # 如果有不足，尝试从其他类别补充
        total_selected = len(selected_indices)
        required = samples_per_cluster
        if total_selected < required:
            remaining = required - total_selected
            # 选择其他类别中距离最近的样本
            other_df = cluster_df[~cluster_df['index'].isin(selected_indices)].sort_values('distance')
            additional = other_df.head(remaining)['index'].tolist()
            selected_indices.extend(additional)
        
        # 获取对应的video_id
        selected_video_ids = [video_ids[idx] for idx in selected_indices]
        representative_video_ids.extend(selected_video_ids)
    
    print(f"总共选择了 {len(representative_video_ids)} 个代表性样本")
    return representative_video_ids

# ----------------------------- #
# 5. 评估聚类效果（可选）
# ----------------------------- #

def evaluate_clustering(embeddings, labels):
    """
    使用轮廓系数评估聚类效果。

    Args:
        embeddings (np.ndarray): 降维后的嵌入向量。
        labels (np.ndarray): 簇标签。

    Returns:
        score (float): 轮廓系数。
    """
    print("计算轮廓系数...")
    score = silhouette_score(embeddings, labels)
    print(f"轮廓系数（Silhouette Score）: {score:.4f}")
    return score

# ----------------------------- #
# 6. 可视化聚类结果（t-SNE）
# ----------------------------- #

def visualize_clusters_tsne(all_embeddings, all_labels, representative_video_ids, video_ids, output_path='tsne_plot.png'):
    """
    使用t-SNE可视化聚类结果，并突出显示选择的代表性样本。

    Args:
        all_embeddings (np.ndarray): 降维后的嵌入向量（所有数据）。
        all_labels (np.ndarray): 簇标签（所有数据）。
        representative_video_ids (List[str]): 选择的代表性video_id列表。
        video_ids (List[str]): 所有video_id列表。
        output_path (str): 保存可视化图的路径。
    """
    print("开始t-SNE降维用于可视化...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=300, verbose=1)
    tsne_results = tsne.fit_transform(all_embeddings)
    print("t-SNE降维完成。")

    # 创建DataFrame用于绘图
    df_tsne = pd.DataFrame({
        'tsne_dim1': tsne_results[:,0],
        'tsne_dim2': tsne_results[:,1],
        'cluster': all_labels
    })

    # 标记代表性样本
    representative_set = set(representative_video_ids)
    df_tsne['is_representative'] = df_tsne['cluster'].apply(
        lambda x: False  # 初始化为False
    )
    # 设置代表性样本的位置
    for idx, vid in enumerate(video_ids):
        if vid in representative_set:
            df_tsne.at[idx, 'is_representative'] = True

    # 优化：为大数据集绘制时，先绘制非代表性样本，再绘制代表性样本
    plt.figure(figsize=(16, 10))
    # 绘制所有非代表性样本
    non_rep = df_tsne[~df_tsne['is_representative']]
    plt.scatter(non_rep['tsne_dim1'], non_rep['tsne_dim2'], c=non_rep['cluster'], cmap='tab10', s=10, alpha=0.3, label='非代表性样本')

    # 绘制代表性样本
    rep = df_tsne[df_tsne['is_representative']]
    plt.scatter(rep['tsne_dim1'], rep['tsne_dim2'], c=rep['cluster'], cmap='tab10', s=50, alpha=0.9, edgecolor='k', label='代表性样本')

    plt.colorbar(label='Cluster Label')
    plt.title('t-SNE 可视化聚类结果（突出显示代表性样本）')
    plt.xlabel('t-SNE 维度 1')
    plt.ylabel('t-SNE 维度 2')
    plt.legend(markerscale=2)
    plt.savefig(output_path, dpi=300)
    plt.show()
    print(f"t-SNE 可视化图已保存到 {output_path}")

# ----------------------------- #
# 7. 保存结果
# ----------------------------- #

def save_representative_video_ids(video_ids, output_path):
    """
    将代表性video_id保存到CSV文件。

    Args:
        video_ids (List[str]): 代表性video_id列表。
        output_path (str): 输出文件路径（.csv）。
    """
    df = pd.DataFrame({'video_id': video_ids})
    df.to_csv(output_path, index=False)
    print(f"已成功保存代表性video_id到 {output_path}")

# ----------------------------- #
# 8. 主函数
# ----------------------------- #

def main():
    # 文件路径（请根据实际情况修改）
    embeddings_jsonl_path = './sentence_embeddings_with_video_id.jsonl'  # 替换为你的嵌入JSONL文件路径
    durations_jsonl_path = '/map-vepfs/dehua/data/image-video-bench/image-video-bench/youtube_video_download_dep.jsonl'  # 时长JSONL文件路径
    output_csv_path = '/map-vepfs/dehua/data/image-video-bench/image-video-bench/representative_video_ids_1100.csv'  # 输出的CSV文件路径
    tsne_output_path = '/map-vepfs/dehua/data/image-video-bench/image-video-bench/tsne_plot.png'  # t-SNE可视化图的输出路径

    # ----------------------------- #
    # 1. 加载数据
    # ----------------------------- #
    emb_video_ids, embeddings = load_embeddings(embeddings_jsonl_path)
    durations_dict = load_durations(durations_jsonl_path)
    video_ids, merged_embeddings, merged_durations = merge_data(emb_video_ids, embeddings, durations_dict)

    # ----------------------------- #
    # 2. 降维（可选）
    # ----------------------------- #
    reduced_embeddings = reduce_dimensionality(merged_embeddings, n_components=100, random_state=42)

    # ----------------------------- #
    # 3. 聚类
    # ----------------------------- #
    num_clusters = 10  # 聚类数量
    kmeans_model, labels = perform_clustering(reduced_embeddings, num_clusters=num_clusters, batch_size=1000, random_state=42)

    # ----------------------------- #
    # 4. 选择代表性样本
    # ----------------------------- #
    # 定义每个簇的时长类别样本数量
    duration_constraints = {
        '5-10': 80,    # 每个簇中选择80个5-10分钟的视频
        '10-30': 20,   # 每个簇中选择20个10-30分钟的视频
        '30+': 10       # 每个簇中选择10个30分钟以上的视频
    }
    samples_per_cluster = sum(duration_constraints.values())  # 80 + 20 + 10 = 110

    representative_video_ids = select_representative_samples(
        video_ids=video_ids,
        embeddings=reduced_embeddings,
        durations=merged_durations,
        labels=labels,
        num_clusters=num_clusters,
        kmeans_model=kmeans_model,
        samples_per_cluster=samples_per_cluster,
        duration_constraints=duration_constraints
    )

    # 检查是否达到目标数量
    if len(representative_video_ids) < 1100:
        print(f"警告：选择的代表性样本数量不足1100，仅选择了{len(representative_video_ids)}个样本。")
    elif len(representative_video_ids) > 1100:
        # 如果超出，截取前1100个
        representative_video_ids = representative_video_ids[:1100]
        print("代表性样本数量超过1100，已截取前1100个样本。")
    else:
        print("成功选择了1100个代表性样本。")

    # ----------------------------- #
    # 5. 评估聚类效果（可选）
    # ----------------------------- #
    evaluate_clustering(reduced_embeddings, labels)

    # ----------------------------- #
    # 6. 可视化聚类结果（t-SNE）
    # ----------------------------- #
    # 由于t-SNE对内存和计算要求较高，确保你的系统有足够的资源
    visualize_clusters_tsne(
        all_embeddings=reduced_embeddings,
        all_labels=labels,
        representative_video_ids=representative_video_ids,
        video_ids=video_ids,
        output_path=tsne_output_path
    )

    # ----------------------------- #
    # 7. 保存结果
    # ----------------------------- #
    save_representative_video_ids(representative_video_ids, output_csv_path)

# if __name__ == "__main__":
#     main()


import csv
import json

def calculate_total_duration(csv_path, jsonl_path):
    """
    计算CSV文件中所有video_id对应视频的总时长。

    参数:
    csv_path (str): 代表视频ID的CSV文件路径。
    jsonl_path (str): 包含视频数据的JSONL文件路径。

    返回:
    int: 所有视频的总时长（秒）。
    """
    # 第一步：读取CSV文件中的video_id并存储在一个集合中
    video_ids = set()
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:
                    video_id = row[0].strip()
                    video_ids.add(video_id)
        print(f"成功读取 {len(video_ids)} 个video_id。")
    except FileNotFoundError:
        print(f"错误：无法找到文件 {csv_path}")
        return 0
    except Exception as e:
        print(f"读取CSV文件时发生错误: {e}")
        return 0

    # 第二步：遍历JSONL文件并统计总时长
    total_duration = 0
    found_videos = 0
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as jsonlfile:
            for line_number, line in enumerate(jsonlfile, 1):
                try:
                    data = json.loads(line)
                    video_id = data.get('video_id')
                    duration = data.get('duration', 0)
                    
                    if video_id in video_ids:
                        # 尝试将duration转换为整数
                        if isinstance(duration, (int, float)):
                            total_duration += duration
                        elif isinstance(duration, str):
                            # 尝试将字符串转换为整数或浮点数
                            try:
                                duration_num = float(duration)
                                total_duration += duration_num
                            except ValueError:
                                print(f"警告：第 {line_number} 行的duration无法转换为数字，跳过。")
                        else:
                            print(f"警告：第 {line_number} 行的duration类型不支持，跳过。")
                        found_videos += 1
                except json.JSONDecodeError:
                    print(f"警告：第 {line_number} 行不是有效的JSON格式，已跳过。")
                except Exception as e:
                    print(f"警告：处理第 {line_number} 行时发生错误: {e}")
    except FileNotFoundError:
        print(f"错误：无法找到文件 {jsonl_path}")
        return 0
    except Exception as e:
        print(f"读取JSONL文件时发生错误: {e}")
        return 0

    print(f"在JSONL文件中找到 {found_videos} 个匹配的视频。")
    return total_duration

def format_duration(seconds):
    """
    将秒数转换为“小时 分钟 秒”的格式。

    参数:
    seconds (float): 总秒数。

    返回:
    str: 格式化后的时间字符串。
    """
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    secs = int(seconds) % 60
    return f"{hours}小时 {minutes}分钟 {secs}秒"

# if __name__ == "__main__":
#     # 定义文件路径
#     csv_path = '/map-vepfs/dehua/data/image-video-bench/image-video-bench/representative_video_ids_1100.csv'
#     jsonl_path = '/map-vepfs/dehua/data/image-video-bench/image-video-bench/youtube_video_download_dep.jsonl'
    
#     # 计算总时长
#     total = calculate_total_duration(csv_path, jsonl_path)
    
#     # 输出结果
#     formatted_total = format_duration(total)
#     print(f"所有视频的总时长为: {formatted_total} ({total} 秒)")


import json
import csv
import os

def load_video_ids_from_json(json_path, key="sampled_id"):
    """
    从JSON文件加载video_id列表。

    Args:
        json_path (str): JSON文件路径。
        key (str): 存储video_id列表的键名。

    Returns:
        Set[str]: 视频ID的集合。
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            sample_datas = json.load(file)
            ids = sample_datas.get(key, [])
            if not isinstance(ids, list):
                raise ValueError(f"键 '{key}' 对应的值不是列表。")
            print(f"从JSON文件中加载了 {len(ids)} 个video_id。")
            return set(ids)
    except FileNotFoundError:
        print(f"错误：无法找到文件 {json_path}")
        return set()
    except json.JSONDecodeError:
        print(f"错误：文件 {json_path} 不是有效的JSON格式。")
        return set()
    except Exception as e:
        print(f"读取JSON文件时发生错误: {e}")
        return set()

def load_video_ids_from_csv(csv_path, column_index=0):
    """
    从CSV文件加载video_id列表。

    Args:
        csv_path (str): CSV文件路径。
        column_index (int): video_id所在的列索引（默认第0列）。

    Returns:
        Set[str]: 视频ID的集合。
    """
    video_ids = set()
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row_number, row in enumerate(reader, 1):
                if len(row) > column_index:
                    video_id = row[column_index].strip()
                    if video_id:
                        video_ids.add(video_id)
                else:
                    print(f"警告：CSV文件的第 {row_number} 行没有足够的列。")
        print(f"从CSV文件中加载了 {len(video_ids)} 个video_id。")
        return video_ids
    except FileNotFoundError:
        print(f"错误：无法找到文件 {csv_path}")
        return set()
    except Exception as e:
        print(f"读取CSV文件时发生错误: {e}")
        return set()

def save_video_ids_to_txt(video_ids, output_dir="."):
    """
    将video_id列表保存到文本文件中，文件名包含视频数量。

    Args:
        video_ids (Set[str]): 视频ID的集合。
        output_dir (str): 输出文件的目录路径（默认为当前目录）。

    Returns:
        str: 保存的文件路径。
    """
    number = len(video_ids)
    filename = f"sample_video_ids_{number}.txt"
    output_path = os.path.join(output_dir, filename)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for vid in sorted(video_ids):
                f.write(f"{vid}\n")
        print(f"已成功保存 {number} 个video_id到 {output_path}")
        return output_path
    except Exception as e:
        print(f"保存文件时发生错误: {e}")
        return ""

def main():
    # 定义文件路径（请根据实际情况修改）
    json_path = '/map-vepfs/dehua/data/image-video-bench/image-video-bench/text_files/sampled_youtube_video_id.json'
    csv_path = '/map-vepfs/dehua/data/image-video-bench/image-video-bench/representative_video_ids_1100.csv'
    output_directory = '/map-vepfs/dehua/data/image-video-bench/image-video-bench/'  # 输出文件的目录

    # ----------------------------- #
    # 1. 加载视频ID
    # ----------------------------- #
    json_video_ids = load_video_ids_from_json(json_path, key="sampled_id")
    csv_video_ids = load_video_ids_from_csv(csv_path, column_index=0)

    # ----------------------------- #
    # 2. 合并并去重
    # ----------------------------- #
    combined_video_ids = json_video_ids.union(csv_video_ids)
    print(f"合并后的视频ID总数（去重）: {len(combined_video_ids)}")

    # ----------------------------- #
    # 3. 保存结果
    # ----------------------------- #
    if combined_video_ids:
        save_video_ids_to_txt(combined_video_ids, output_dir=output_directory)
    else:
        print("没有要保存的video_id。")

if __name__ == "__main__":
    main()
