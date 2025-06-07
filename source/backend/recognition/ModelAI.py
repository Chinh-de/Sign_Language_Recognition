
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import KFold
from torch.utils.data import DataLoader, random_split, Dataset
from torch.nn.utils.rnn import pad_sequence
from torch.optim.lr_scheduler import ReduceLROnPlateau

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
import json
import math
import itertools
import time
from datetime import datetime
from tqdm import tqdm

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(max_len, dtype=torch.float32).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:, :x.shape[1], :]
        return self.dropout(x)

class Sign2PoseTransformer(nn.Module):
    def __init__(self, input_dim=171, d_model=256, 
                 nhead=8, num_encoder_layers=3, num_decoder_layers=3, 
                 dim_feedforward=2048, dropout=0.2, num_classes=100):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout=dropout)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, 
                                                   dim_feedforward=dim_feedforward, dropout=dropout, 
                                                   batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_encoder_layers)
        decoder_layer = nn.TransformerDecoderLayer(d_model=d_model, nhead=nhead, 
                                                   dim_feedforward=dim_feedforward, dropout=dropout, 
                                                   batch_first=True)
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_decoder_layers)
        self.class_query = nn.Parameter(torch.randn(1, 1, d_model))
        self.fc_out = nn.Linear(d_model, num_classes)
    
    def forward(self, src):
        batch_size = src.size(0)
        src_key_padding_mask = (src.sum(dim=2) == 0)
        src = self.input_proj(src)
        src = self.pos_encoder(src)
        memory = self.encoder(src, src_key_padding_mask=src_key_padding_mask)
        class_query = self.class_query.expand(batch_size, 1, -1) 
        out = self.decoder(tgt=class_query, memory=memory, memory_key_padding_mask=src_key_padding_mask)     
        out = out.squeeze(1)            
        logits = self.fc_out(out)
        
        return logits