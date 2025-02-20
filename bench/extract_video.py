urls = [
    "2nt080o5xkc&t=282s",
    "zJtkWV3-XoY&t=38s",
    "zuzvxS3bA3c",
    "t8nykVWxWyc",
    "oZ7SPK3rGT4",
    "eSCfJHcqgws&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=4",
    "3Ojk9xbCHBs&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=7",
    "FDJzjRhjsgI&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=14",
    "Hnx-H5NbD-k&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=15",
    "h6CrAR9hIPQ&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=24",
    "qc3aHNBSnso&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=25",
    "sknk3qOD4Ts&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=26",
    "r80N3Eg5WKg&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=32",
    "J435mzrqLek&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=39",
    "rRQ4pPzTF_Q&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=42",
    "XPxxgiOVm7k&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=44",
    "NEt4eAdIL_k&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=50",
    "sl7NV8FCXbc&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=52",
    "9MW9V5WtFSo&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=54",
    "ouvWe8d744E&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=60",
    "Wej0bImDFa8&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=62",
    "c-ocUGFQRTk&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=63",
    "JbLvywq0Yww&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=64",
    "6YAQDzQLMFE&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=66",
    "1UYkz2UAWY8&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=67",
    "kXQen1kXAls&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=75",
    "aLtVC_FqkC8&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=76",
    "VwI2sWqQIwc&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=85",
    "RCpF_oNHXb8&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=88",
    "8rGdMm5VSm0&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=97",
    "dADKV6gqUJc&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=110",
    "TKaic6NH0vE&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=147",
    "NkhnFseP4RA&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=153",
    "trRMuyCt9gg&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=175",
    "Ez6Yrnh4w6k&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=158"
]



# 原始 URL 列表
urls = [
    "mVhZsu4RRZ8",
    "DRupZvUXGG4",
    "cOdynPv8cok",
    "_w92IZyVJxg",
    "kToFKqsCVLQ",
    "eVsXVzSse8I",
    "k-G_o8FmIWA",
    "A9PSI0IzPqw",
    "fJUaISAPSVg",
    "-WzB5wqpkbg"
]

# 提取视频 ID
video_ids = [url.split('v=')[1].split('&')[0] for url in urls]

extracted_list = []
for url in urls:
    # 将 URL 按 "watch?v=" 分割，取分割后第二部分
    parts = url.split("watch?v=")
    if len(parts) == 2:
        extracted_list.append(parts[1])
    else:
        # 如果分割后不是两个部分，说明 URL 格式不同，可自行处理
        extracted_list.append("URL 格式不符合预期")

# 打印提取结果
for item in extracted_list:
    print(f'"{item}",')

# 如果需要将结果保存在列表中，直接使用 extracted_list 即可
