#!/bin/bash
#!/bin/bash

# 设置代理
# export http_proxy=http://100.64.117.161:3128
# export https_proxy=http://100.64.117.161:3128
# 检查是否传入参数，没有传入则使用默认值
GPU_ID=${1:-0}        # 第一个参数：GPU ID, 默认使用 GPU 0
HAS_IMAGE=${2:-1}   # 第二个参数：是否包含图像, 默认是 True
NFRAMES=${3:-32}       # 第三个参数：帧数, 默认是 32
QUESTION_FILE=${4:-None}
QUESTION_FILE=${4:-"/Users/dehua/code/image-video-bench/res/all_data_v3.jsonl"}
OUTPUT_DIR=${5:-'/Users/dehua/code/image-video-bench/outputs'}
video_jsonl_path="./video_frames.jsonl"
duration_path="./video_duration.jsonl"
json_path="/Users/dehua/code/image-video-bench/video_conversation.json"
# Default OUTPUT_FILE path
OUTPUT_FILE="${OUTPUT_DIR}/gpt_${NFRAMES}.jsonl"

# Check if HAS_IMAGE is false and modify OUTPUT_FILE accordingly
if [ "$HAS_IMAGE" = 0 ]; then
    OUTPUT_FILE="${OUTPUT_DIR}/gpt_${HAS_IMAGE}_${NFRAMES}.jsonl"
fi

# 设置 PYTHONPATH 并运行 Python 脚本，传递命令行参数
export PYTHONPATH=/map-vepfs/dehua/code/Long-Bench
python inference_gpt_run.py \
    --config_path=gpt.yaml \
    --has_image=$HAS_IMAGE \
    --nframes=$NFRAMES \
    --question_file=$QUESTION_FILE \
    --output_file=$OUTPUT_FILE \
    --video_jsonl_path=$video_jsonl_path \
    --duration_path=$duration_path \
    --output_file=$OUTPUT_FILE