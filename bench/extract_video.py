urls = [
    "https://www.youtube.com/watch?v=2nt080o5xkc&t=282s",
    "https://www.youtube.com/watch?v=zJtkWV3-XoY&t=38s",
    "https://www.youtube.com/watch?v=zuzvxS3bA3c",
    "https://www.youtube.com/watch?v=t8nykVWxWyc",
    "https://www.youtube.com/watch?v=oZ7SPK3rGT4",
    "https://www.youtube.com/watch?v=eSCfJHcqgws&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=4",
    "https://www.youtube.com/watch?v=3Ojk9xbCHBs&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=7",
    "https://www.youtube.com/watch?v=FDJzjRhjsgI&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=14",
    "https://www.youtube.com/watch?v=Hnx-H5NbD-k&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=15",
    "https://www.youtube.com/watch?v=h6CrAR9hIPQ&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=24",
    "https://www.youtube.com/watch?v=qc3aHNBSnso&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=25",
    "https://www.youtube.com/watch?v=sknk3qOD4Ts&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=26",
    "https://www.youtube.com/watch?v=r80N3Eg5WKg&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=32",
    "https://www.youtube.com/watch?v=J435mzrqLek&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=39",
    "https://www.youtube.com/watch?v=rRQ4pPzTF_Q&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=42",
    "https://www.youtube.com/watch?v=XPxxgiOVm7k&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=44",
    "https://www.youtube.com/watch?v=NEt4eAdIL_k&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=50",
    "https://www.youtube.com/watch?v=sl7NV8FCXbc&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=52",
    "https://www.youtube.com/watch?v=9MW9V5WtFSo&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=54",
    "https://www.youtube.com/watch?v=ouvWe8d744E&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=60",
    "https://www.youtube.com/watch?v=Wej0bImDFa8&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=62",
    "https://www.youtube.com/watch?v=c-ocUGFQRTk&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=63",
    "https://www.youtube.com/watch?v=JbLvywq0Yww&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=64",
    "https://www.youtube.com/watch?v=6YAQDzQLMFE&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=66",
    "https://www.youtube.com/watch?v=1UYkz2UAWY8&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=67",
    "https://www.youtube.com/watch?v=kXQen1kXAls&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=75",
    "https://www.youtube.com/watch?v=aLtVC_FqkC8&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=76",
    "https://www.youtube.com/watch?v=VwI2sWqQIwc&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=85",
    "https://www.youtube.com/watch?v=RCpF_oNHXb8&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=88",
    "https://www.youtube.com/watch?v=8rGdMm5VSm0&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=97",
    "https://www.youtube.com/watch?v=dADKV6gqUJc&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=110",
    "https://www.youtube.com/watch?v=TKaic6NH0vE&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=147",
    "https://www.youtube.com/watch?v=NkhnFseP4RA&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=153",
    "https://www.youtube.com/watch?v=trRMuyCt9gg&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=175",
    "https://www.youtube.com/watch?v=Ez6Yrnh4w6k&list=PLoaTLsTsV3hNkTxJfircjW3etUDZIYMXX&index=158"
]

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
