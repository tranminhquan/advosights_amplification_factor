import numpy as np
import pickle
import matplotlib.pyplot as plt

import torch
from torch_geometric.data import Data
from torch_geometric.utils import degree
from torch.utils.data import DataLoader
from collections import OrderedDict
import torch_geometric.visualization
import time

import torch_geometric.nn as nn
import torch.nn.functional as F
import torch_geometric.transforms as T

from sklearn.manifold import TSNE
import sklearn
from torch_geometric.nn import GCNConv, GAE, VGAE

from afadvo.utils.visualize import visualize_tsne

class VGAEEncoder(torch.nn.Module):
    def __init__(self, n_node_atts, emb_dim):
        super(VGAEEncoder, self).__init__()
        self.conv1 = GCNConv(n_node_atts, 2 * emb_dim, cached=True)
        self.conv_mu = GCNConv(2 * emb_dim, emb_dim, cached=True)
        self.conv_logvar = GCNConv(2 * emb_dim, emb_dim, cached=True)
        
    def forward(self, x, edge_index, edge_weight):
        x = F.relu(self.conv1(x, edge_index, edge_weight=edge_weight))
        return self.conv_mu(x, edge_index, edge_weight=edge_weight), self.conv_logvar(x, edge_index, edge_weight=edge_weight)

class VGAEEmb():
    def __init__(self, data, emb_dim=128, save_path=None, **kwargs):
        if type(data) is str:
            self.data = torch.load(data)
        elif type(data) is torch_geometric.data.Data:
            self.data = data
            
        self.dim = emb_dim
        self.save_path = save_path
        
        self.n_node_atts = self.data.x.shape[1]
        self.n_edge_atts = self.data.edge_attr.shape[1]
        
        self.scaler = sklearn.preprocessing.StandardScaler()
        
        # cal edge weight and normalize data
        self.cal_edge_weight()
        
        # preprocessing
        scale = kwargs['scale'] if 'scale' in kwargs else False
        normalize = kwargs['normalize'] if 'normalize' in kwargs else False
        print('- Preprocess graph data: ')
        print('\t * Scale = ', scale)
        print('\t * Normalize = ', normalize)
        
        self.preprocess(scale=scale, normalize=normalize)
        self.data.x = torch.from_numpy(self.scaler.fit_transform(self.data.x))
    

        # split test
#         self.data = train_test_split_edges(self.data)
        
        # set model
        self.model = torch_geometric.nn.VGAE(VGAEEncoder(self.n_node_atts, self.dim))
        
        
    def preprocess(self, scale, normalize):
        # node attribute
        if scale:
            self.data.x = torch.from_numpy(sklearn.preprocessing.scale(self.data.x))
        if normalize:
            self.data.x = torch.from_numpy(sklearn.preprocessing.normalize(self.data.x))
            
    def cal_edge_weight(self):
        '''
        Function defines how to cal weight of edge from reactions, comments and shares
        - current version: f = #reactions + #comments + #shares / 3
        '''
#         self.data.edge_attr = torch.mean(self.data.edge_attr, axis=1)
        self.data.edge_attr = 0.6*self.data.edge_attr[:,0] + 0.3*self.data.edge_attr[:,1] + 0.1*self.data.edge_attr[:,2]
        
    
    def train(self, epochs, device, optim='adam', **kwargs):
        
        self.model = self.model.to(device)
        x, edge_index, edge_att = self.data.x.float().to(device), self.data.edge_index.to(device), self.data.edge_attr.float().to(device)        
#         x, train_pos_edge_index, edge_att = self.data.x.to(device), self.data.train_pos_edge_index.to(device), self.data.edge_attr.float().to(device)
        
        lr = kwargs['lr'] if 'lr' in kwargs else 0.001
        if optim == 'adam':
            optim = torch.optim.Adam(self.model.parameters(), lr=lr)
        elif optim == 'sgd':
            optim = torch.optim.SGD(self.model.parameters(), lr=lr)
        
        print('Training GAE with epochs= ', epochs, ', optim=', optim, '\n -----------------')
        
        if device.type == 'cuda':
            print('*GPU is activated')
        else:
            print('*CPU is activated')
        
        # train
        start_time = time.time()
        hloss = []
        min_loss = 1000.
        
        for epoch in range(epochs):
            loss = self.single_train(x, edge_index, edge_att, optim, device)
#             loss = self.single_train2(x, train_pos_edge_index, optim, device)
            hloss.append(loss)
            
#             auc, ap = self.test(x, self.data.test_pos_edge_index, self.data.test_neg_edge_index, train_pos_edge_index)
            
            print('- Epoch: {:02d}, Loss: {:.4f}, AUC: {:.4f}, AP: {:.4f}'.format(epoch, loss, 0, 0))
            
            if not self.save_path is None:
                if loss < min_loss:
                    min_loss = loss
                    torch.save(self.model, self.save_path)
                    print('\t **Updated checkpoint**')
                    
        print('Training complete.')
        print('\n------------------------------\n')
        print('Training time: ', time.time() - start_time)
        
        if not self.save_path is None:
            print('Minimum loss: ', min_loss)
        else:
            print('Latest loss: ', loss)
        
        return hloss
    
    
    def single_train(self, x, edge_index, edge_att, optim, device):
        '''
        Train Node2Vec in a single epoch
        '''
        self.model.train()
        optim.zero_grad()
        
        z = self.model.encode(x, edge_index, edge_att)
        loss = self.model.recon_loss(z, edge_index)
        loss.backward()
        optim.step()
        
        return loss.item()
    
    def single_train2(self, x, edge_index, optim, device):
        '''
        Train Node2Vec in a single epoch
        '''
        self.model.train()
        optim.zero_grad()
        
        z = self.model.encode(x, edge_index)
        loss = self.model.recon_loss(z, edge_index)
        loss.backward()
        optim.step()
        
        return loss.item()
    
    def test(self, x, pos_edge_index, neg_edge_index, train_pos_edge_index):
        self.model.eval()
        with torch.no_grad():
            z = self.model.encode(x, train_pos_edge_index)
        return self.model.test(z, pos_edge_index, neg_edge_index)
    
    def predict(self, data, device, save_emb_path=None, **kwargs):
        if self.save_path is None:
            test_model = self.model
        else:
            test_model = torch.load(self.save_path)
            
        if type(data) is str:
            data = torch.load(data)
        
        scale = kwargs['scale'] if 'scale' in kwargs else False
        normalize = kwargs['normalize'] if 'normalize' in kwargs else False
        
#         if scale:
#             data.x = torch.from_numpy(sklearn.preprocessing.scale(data.x))
#         if normalize:
#             data.x = torch.from_numpy(sklearn.preprocessing.normalize(data.x))
            
        print('Normalized')
        self.data.x = torch.from_numpy(self.scaler.transform(self.data.x))
            
        z = test_model.encode(data.x.float().to(device), data.edge_index.to(device), data.edge_attr.to(device))
        
        if not save_emb_path is None:
            with open(save_emb_path, 'wb') as dt:
                pickle.dump(z, dt)
                
        return z
    
    def visualize(self, z, algorithm='tsne', n_dim=2, figsize=(150,150), save_emb_path=None, save_fig_path=None):
        '''
        Visualize vector space by given alogrithm
        '''
        if type(z) is str:
            with open(z, 'rb') as dt:
                z = pickle.load(dt)
            
        visualize_tsne(z, n_dim, figsize, save_emb_path, save_fig_path)