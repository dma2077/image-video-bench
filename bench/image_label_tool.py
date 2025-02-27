import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import json

class ImageLabelingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeling Tool")

        # 创建三个框架：用于加载文件夹的框架，用于显示图像的框架，用于放置按钮的框架
        self.label_frame = tk.Frame(root)
        self.label_frame.pack()

        self.image_frame = tk.Frame(root)
        self.image_frame.pack()

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        # 创建一个按钮用于加载文件夹
        self.load_folder_button = tk.Button(self.label_frame, text="Load Folder", command=self.load_folder)
        self.load_folder_button.pack()

        # 创建一个标签用于显示图像
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack()

        # 定义标注标签
        self.labels = ["否", "是"]

        # 初始化图像列表和当前图像索引
        self.image_list = []
        self.current_image_index = 0
        self.annotations = {}

        # 绑定键盘数字键
        self.root.bind("<Key>", self.on_key_press)


    def load_folder(self):
        # 弹出文件夹选择对话框
        folder_path = filedialog.askdirectory()
        if folder_path:
            # 获取文件夹及其所有子目录中所有图像文件路径
            self.image_list = []
            for root, _, files in os.walk(folder_path):  # 使用 os.walk 遍历子目录
                for f in files:
                    if f.lower().endswith(('png', 'jpg', 'jpeg')):
                        self.image_list.append(os.path.join(root, f))

            self.current_image_index = 0
            self.annotations = {}

            # 如果存在之前的标注结果文件，读取其中的内容
            if os.path.exists('result.json'):
                with open('result.json', 'r', encoding='utf-8') as f:
                    self.annotations = json.load(f)

            # 跳过已经标注的图像
            self.image_list = [img for img in self.image_list if os.path.basename(img) not in self.annotations]

            # 显示第一张未标注的图像
            self.show_image()

    def show_image(self):
        # 显示当前图像
        if self.image_list:
            image_path = self.image_list[self.current_image_index]
            image = Image.open(image_path)
            image = image.resize((500, 500), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo

    def label_image(self, label):
        # 对当前图像进行标注
        if self.image_list:
            image_path = self.image_list[self.current_image_index]
            self.annotations[os.path.basename(image_path)] = label

            # 每次标注后立即保存结果到JSON文件
            self.save_annotations()

            self.current_image_index += 1
            if self.current_image_index < len(self.image_list):
                self.show_image()
            else:
                messagebox.showinfo("Info", "所有图像已标注完毕，结果保存至result.json")

    def save_annotations(self):
        # 将标注结果保存到JSON文件
        with open('result.json', 'w', encoding='utf-8') as f:
            json.dump(self.annotations, f, ensure_ascii=False, indent=4)

    def on_key_press(self, event):
        # 根据按下的键进行标注
        if event.char in "10":
            index = int(event.char)
            label = self.labels[index]
            self.label_image(label)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLabelingApp(root)
    root.mainloop()
