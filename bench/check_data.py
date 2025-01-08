import json
# 检查生成的JSON文件中是否有重复元素


output_file = '/Users/dehua/code/image-video-bench/text_files/updated_sampled_videos_ids_0109.json'
# 检查生成的JSON文件中是否有重复元素，并移除索引大于1100的重复项
def check_and_remove_duplicates(json_file):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            sampled_ids = data.get("sampled_id", [])
            duplicates = {}
            for i, item in enumerate(sampled_ids):
                if sampled_ids.count(item) > 1:
                    if item not in duplicates:
                        duplicates[item] = []
                    duplicates[item].append(i)
            print(duplicates)
            # 移除索引大于1100的重复项
            to_remove = set()
            for dup, indices in duplicates.items():
                for idx in indices:
                    if idx > 1100:
                        to_remove.add(idx)

            # 创建新的列表，移除需要删除的索引
            sampled_ids = [item for i, item in enumerate(sampled_ids) if i not in to_remove]

        # # 将更新后的数据写回文件
        with open(json_file, 'w') as f:
            json.dump({"sampled_id": sampled_ids}, f, indent=4)

        print(f"Removed {len(to_remove)} items with indices > 1100.")
    except Exception as e:
        print(f"Error checking duplicates in {json_file}: {e}")

check_and_remove_duplicates(output_file)

print("Processing complete!")
