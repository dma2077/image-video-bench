import os
import json
import random
from collections import defaultdict

# Step 1: Load the video data and apply the initial filtering (length and quality)
video_datas = []
with open('./youtube_video_download_dep.jsonl', 'r', encoding='utf-8') as file:
    for line in file:
        try:
            data = json.loads(line)
            duration = int(data["duration"])  # convert duration to int (seconds)
            # Filter: duration >= 300 (5 minutes), and quality not 720p/720p60
            if duration >= 300 and data["quality"] not in {'720p', '720p60'}:
                video_datas.append(data)
        except (KeyError, ValueError, json.JSONDecodeError):
            # Skip entries with missing or invalid duration/quality or malformed JSON
            continue

print(f"Total videos after initial filtering: {len(video_datas)}")

# Step 2: Get all .mp4 files from the directory (file names without .mp4 extension)
directory_path = r"E:\Code\image-video-bench\videos\examples\youtube_0518"
try:
    mp4_files = {os.path.splitext(file)[0] for file in os.listdir(directory_path) if file.endswith('.mp4')}
except FileNotFoundError:
    raise FileNotFoundError(f"The directory {directory_path} does not exist.")

print(f"Total .mp4 files found: {len(mp4_files)}")

# Step 3: Extract video_id from video_datas
video_ids = {data["video_id"] for data in video_datas}

# Step 4: Find intersection of video_ids with the filenames (without .mp4)
intersection_ids = video_ids.intersection(mp4_files)

print(f"Number of videos in intersection: {len(intersection_ids)}")

# Step 5: Categorize intersection videos by duration ranges
range_5_10 = []
range_10_30 = []
range_30_plus = []

intersection_videos = [video for video in video_datas if video["video_id"] in intersection_ids]

for video in intersection_videos:
    duration = int(video["duration"])
    if 300 <= duration < 600:
        range_5_10.append(video)
    elif 600 <= duration < 1800:
        range_10_30.append(video)
    elif duration >= 1800:
        range_30_plus.append(video)

# Step 6: Print current counts in each range
print(f"Current counts in intersection:")
print(f"5-10 minutes: {len(range_5_10)}")
print(f"10-30 minutes: {len(range_10_30)}")
print(f"30+ minutes: {len(range_30_plus)}")

# Step 7: Define target counts
target_5_10 = 1000
target_10_30 = 150
target_30_plus = 50

# Calculate how many more videos we need to add to each category
needed_5_10 = target_5_10 - len(range_5_10)
needed_10_30 = target_10_30 - len(range_10_30)
needed_30_plus = target_30_plus - len(range_30_plus)

print(f"Needed videos to add:")
print(f"5-10 minutes: {needed_5_10}")
print(f"10-30 minutes: {needed_10_30}")
print(f"30+ minutes: {needed_30_plus}")

# Ensure that needed counts are not negative
needed_5_10 = max(needed_5_10, 0)
needed_10_30 = max(needed_10_30, 0)
needed_30_plus = max(needed_30_plus, 0)

# Step 8: Prepare to sample additional videos from video_datas excluding intersection
additional_pool = [video for video in video_datas if video["video_id"] not in intersection_ids]

# Categorize additional_pool videos by duration ranges
additional_5_10_pool = [video for video in additional_pool if 300 <= int(video["duration"]) < 600]
additional_10_30_pool = [video for video in additional_pool if 600 <= int(video["duration"]) < 1800]
additional_30_plus_pool = [video for video in additional_pool if int(video["duration"]) >= 1800]

# Check if there are enough videos to sample
if len(additional_5_10_pool) < needed_5_10:
    raise ValueError(f"Not enough videos to sample for 5-10 minutes range. Needed: {needed_5_10}, Available: {len(additional_5_10_pool)}")
if len(additional_10_30_pool) < needed_10_30:
    raise ValueError(f"Not enough videos to sample for 10-30 minutes range. Needed: {needed_10_30}, Available: {len(additional_10_30_pool)}")
if len(additional_30_plus_pool) < needed_30_plus:
    raise ValueError(f"Not enough videos to sample for 30+ minutes range. Needed: {needed_30_plus}, Available: {len(additional_30_plus_pool)}")

# Randomly sample the needed number of videos from each pool
additional_videos_5_10 = random.sample(additional_5_10_pool, needed_5_10) if needed_5_10 > 0 else []
additional_videos_10_30 = random.sample(additional_10_30_pool, needed_10_30) if needed_10_30 > 0 else []
additional_videos_30_plus = random.sample(additional_30_plus_pool, needed_30_plus) if needed_30_plus > 0 else []

# Step 9: Combine the intersection videos with the additional sampled videos
sampled_videos = (
    intersection_videos +
    additional_videos_5_10 +
    additional_videos_10_30 +
    additional_videos_30_plus
)

# Shuffle the sampled_videos to ensure randomness
random.shuffle(sampled_videos)

# Step 10: Check the total number of sampled videos
print(f"Total sampled videos: {len(sampled_videos)}")

# Verify that the total matches the target
expected_total = len(intersection_videos) + needed_5_10 + needed_10_30 + needed_30_plus
if len(sampled_videos) != expected_total:
    raise ValueError("The total number of sampled videos does not match the expected count.")

# Step 11: Calculate the average duration of sampled videos
total_duration = sum(int(video["duration"]) for video in sampled_videos)
average_duration = total_duration / len(sampled_videos) if sampled_videos else 0

print(f"Average duration of sampled videos: {average_duration:.2f} seconds")

# Step 12: Print the distribution of video durations in the sample
duration_distribution = defaultdict(int)
for video in sampled_videos:
    duration = int(video["duration"])
    if 300 <= duration < 600:
        duration_distribution['5-10 minutes'] += 1
    elif 600 <= duration < 1800:
        duration_distribution['10-30 minutes'] += 1
    elif duration >= 1800:
        duration_distribution['30+ minutes'] += 1

print("Duration distribution in sampled videos:")
for range_label in ['5-10 minutes', '10-30 minutes', '30+ minutes']:
    print(f"{range_label}: {duration_distribution[range_label]} videos")

# Step 13: Save the sampled video IDs into a text file
output_file_path = "./sampled_youtube_video_id.txt"
with open(output_file_path, 'w', encoding='utf-8') as file:
    for video in sampled_videos:
        file.write(f"{video['video_id']}\n")

print(f"Sampled video IDs have been saved to '{output_file_path}'.")
