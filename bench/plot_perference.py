import matplotlib.pyplot as plt
import numpy as np

# 数据，包括添加的'total'类别
categories = [
    "Total", "Reverse Existence", "NLI", "Constrained OCR", "Keyframe extraction", "Details Event",
    "Space-time computing", "Counting", "Spatial relationship", "Temporal Reasoning", 
    "Existence", "Summary", "Attribute Change", "Instruction manual"
]

# 每种设置下的具体类别性能
noimage_scores = [
    0.20859, 0.178, 0.190, 0.371, 0.208, 0.260, 0.228, 0.180, 0.346, 0.167, 0.043, 0.167, 0.214, 0.155
]
video_first_scores = [
    0.2863, 0.205, 0.601, 0.396, 0.195, 0.405, 0.131, 0.213, 0.431, 0.122, 0.280, 0.278, 0.262, 0.294
]
image_first_scores = [
    0.2434, 0.174, 0.418, 0.371, 0.160, 0.300, 0.196, 0.199, 0.405, 0.067, 0.161, 0.250, 0.262, 0.245
]

# 设置柱状图位置
x = np.arange(len(categories))  # 类别数量
width = 0.25  # 每个柱子的宽度

# 创建图形
fig, ax = plt.subplots(figsize=(12, 8))

# 绘制柱状图
bars_video_first = ax.bar(x - width, video_first_scores, width, label='video_first', color='tab:orange', alpha=0.8)
bars_image_first = ax.bar(x, image_first_scores, width, label='image_first', color='tab:green', alpha=0.8)
bars_noimage = ax.bar(x + width, noimage_scores, width, label='noimage', color='tab:blue', alpha=0.8)

# 添加每个柱子的文本标签，显示正确率
def add_text(bars, values):
    pass
    # for bar, value in zip(bars, values):
    #     ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f'{value:.3f}', 
    #             ha='center', va='bottom', fontsize=10, color='black')
        # ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.10, f'{value:.3f}', 
        #         ha='center', va='top', fontsize=10, color='white', alpha=0.5)

# 添加标签到柱状图
add_text(bars_video_first, video_first_scores)
add_text(bars_image_first, image_first_scores)
add_text(bars_noimage, noimage_scores)

# 设置轴标签和标题
ax.set_xlabel('Categories', fontsize=12)
ax.set_ylabel('Accuracy', fontsize=12)
ax.set_title('Model Performance Comparison', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=45, ha="right", fontsize=10)

# 添加图例
ax.legend()

# 显示网格
ax.grid(True, linestyle='--', alpha=0.7)

# 显示图形
plt.tight_layout()
plt.savefig('model_performance_comparison.png', dpi=300)
