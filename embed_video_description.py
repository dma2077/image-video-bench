import os
import torch
import json
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from torch.utils.data import DataLoader, Dataset
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler
from tqdm import tqdm  # 导入tqdm

# 需要的参数
batch_size = 32
num_epochs = 1
output_file_path = "./sentence_embeddings_new.jsonl"

# 配置分布式环境
def setup(rank, world_size):
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    dist.init_process_group("gloo", rank=rank, world_size=world_size)  # 修改后端为gloo

def cleanup():
    dist.destroy_process_group()

# 定义Dataset
class SentenceDataset(Dataset):
    def __init__(self, sentences, video_ids, tokenizer):
        self.sentences = sentences
        self.video_ids = video_ids
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        sentence = self.sentences[idx]
        video_id = self.video_ids[idx]
        encoded_input = self.tokenizer(sentence, padding='max_length', truncation=True, max_length=128, return_tensors='pt')
        return encoded_input, video_id

# Mean Pooling Function
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# 计算嵌入的函数
def compute_embeddings(dataloader, model, device, rank, world_size):
    all_embeddings = []
    all_video_ids = []
    model.eval()
    with torch.no_grad():
        for batch in tqdm(dataloader, desc=f"Processing GPU {rank}", dynamic_ncols=True):
            inputs, video_ids = batch
            input_ids = inputs['input_ids'].squeeze(1).to(device)
            attention_mask = inputs['attention_mask'].squeeze(1).to(device)
            model_output = model(input_ids, attention_mask=attention_mask)
            sentence_embeddings = mean_pooling(model_output, attention_mask)
            sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
            
            # # 打印嵌入的形状（可选）
            # print(f"Rank {rank} - Sentence Embeddings Shape: {sentence_embeddings.shape}")
            
            all_embeddings.append(sentence_embeddings.cpu())
            all_video_ids.extend(video_ids)  # 使用 extend 而不是 append
    
    return torch.cat(all_embeddings, dim=0), all_video_ids

# 保存结果到文件
def save_results(rank, embeddings, video_ids):
    if rank == 0:  # 只在rank 0的进程中写入文件
        with open(output_file_path, 'a', encoding='utf-8') as file:
            for emb, video_id in zip(embeddings, video_ids):
                result = {"video_id": video_id, "embedding": emb.tolist()}
                json.dump(result, file)
                file.write("\n")

# 使用gather_object收集所有卡的结果
def gather_results(rank, world_size, embeddings, video_ids, device):
    # 先确保所有张量都在正确的设备上（GPU）
    embeddings = embeddings.to(device)
    
    # 使用张量收集嵌入向量
    gathered_embeddings = [torch.zeros_like(embeddings) for _ in range(world_size)]
    dist.all_gather(gathered_embeddings, embeddings)
    all_embeddings = torch.cat(gathered_embeddings, dim=0)
    
    # 使用 gather_object 收集 video_ids 到 rank 0
    if rank == 0:
        gathered_video_ids = [None for _ in range(world_size)]
    else:
        gathered_video_ids = None
    
    # 确保所有进程达到此点
    dist.barrier()
    
    # 使用 gather_object 收集 video_ids
    dist.gather_object(video_ids, gathered_video_ids, dst=0)
    
    if rank == 0:
        # 合并所有 video_ids
        all_video_ids = []
        for ids in gathered_video_ids:
            all_video_ids.extend(ids)
    else:
        all_video_ids = []
    
    return all_embeddings, all_video_ids

def main(rank, world_size):
    # 初始化分布式环境
    setup(rank, world_size)

    # 获取当前设备
    device = torch.device(f'cuda:{rank}') if torch.cuda.is_available() else torch.device('cpu')

    # 加载模型和tokenizer
    tokenizer = AutoTokenizer.from_pretrained('/map-vepfs/models/sentence-transformers/all-roberta-large-v1')
    model = AutoModel.from_pretrained('/map-vepfs/models/sentence-transformers/all-roberta-large-v1').to(device)

    # 使用DistributedDataParallel包裹模型
    model = DDP(model, device_ids=[rank] if torch.cuda.is_available() else None)

    # 加载数据
    sentences = []
    video_ids = []
    with open("./sampled_youtube_video.jsonl", 'r', encoding='utf-8') as file:
        for data in file:
            data = json.loads(data)
            sentences.append(data["description"])
            video_ids.append(data["video_id"])

    # 数据集和数据加载器
    dataset = SentenceDataset(sentences, video_ids, tokenizer)
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank, shuffle=False)
    dataloader = DataLoader(dataset, batch_size=batch_size, sampler=sampler, num_workers=4)

    # 计算嵌入
    sentence_embeddings, video_ids = compute_embeddings(dataloader, model, device, rank, world_size)

    # 使用gather_results收集所有卡的结果
    all_embeddings, all_video_ids = gather_results(rank, world_size, sentence_embeddings, video_ids, device)

    # 保存结果
    save_results(rank, all_embeddings, all_video_ids)

    # 清理分布式环境
    cleanup()

# 启动多进程
if __name__ == "__main__":
    world_size = torch.cuda.device_count()  # 自动获取GPU数量
    if world_size < 1:
        raise ValueError("No GPUs available for distributed processing.")
    torch.multiprocessing.spawn(main, args=(world_size,), nprocs=world_size, join=True)
