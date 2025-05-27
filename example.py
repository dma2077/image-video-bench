import os
# 通过 pip install volcengine-python-sdk[ark] 安装方舟SDK
from volcenginesdkarkruntime import Ark

# 从环境变量中获取API Key
client = Ark(
    api_key='ec394fe9-8cb4-40ae-8155-06108b06a2b2',
    )

response = client.chat.completions.create(
    model="doubao-1-5-vision-pro-32k-250115",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "支持输入是图片的模型系列是哪个？同时，豆包应用场景有哪些？"},
                {"type": "image_url","image_url": {"url":  "https://ark-project.tos-cn-beijing.volces.com/doc_image/ark_demo_img_1.png"}},
                {"type": "image_url","image_url": {"url":  "https://ark-project.tos-cn-beijing.volces.com/doc_image/ark_demo_img_2.png"}},
            ],
        }
    ],
)

print(response.choices[0])