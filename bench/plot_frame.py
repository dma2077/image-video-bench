import matplotlib.pyplot as plt

# 假设字典数据如下（根据您的要求和数据进行调整）
data = {
    "32": {
        "total": 0.2844,
    },
    "64": {
        "total": 0.2418,
    },
    "128": {
        "total": 0.2588,
    }
}

# 提取帧率和对应的模型性能数据
frame_rates = list(data.keys())
total_performance = [data[frame_rate]["total"] for frame_rate in frame_rates]

# 绘制柱状图
plt.figure(figsize=(8, 6))
plt.bar(frame_rates, total_performance, color='skyblue')

# 添加图表标签和标题
plt.title("Performance vs Frames")
plt.xlabel("Frames")
plt.ylabel("Accuracy")

# 显示图表
plt.tight_layout()
plt.show()