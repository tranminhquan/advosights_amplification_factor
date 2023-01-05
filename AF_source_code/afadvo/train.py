'''Training embedding model (phase 1)'''
import argparse
import torch
from nn.models.vgae import VGAEEmb
from nn.models.vae_agc import VGAEAGCEmb
from nn.models.gae import GAEEmb
from nn.models.node2vec import Node2VecEmb
import pickle

import warnings

# Ignore warnings
warnings.filterwarnings("ignore")

def train(model_type, data, savepath, dim, gpu, epochs, optimizer, learningrate, monitor, historypath):

    # setting device
    if gpu is True:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if str(device) != 'cuda':
            print('GPU is not available, switch to CPU')
        else:
            print('GPU is activated')
    else:
        device = torch.device('cpu')
    

    print('Type of model: ', model_type)
    history = None
    if model_type == 'vgae':
        model = VGAEEmb(data, dim, savepath)
        history = model.train(int(epochs), device, optimizer, lr=learningrate, monitor=monitor)

    elif model_type == 'gae':
        model = GAEEmb(data, dim, savepath)
        history = model.train(int(epochs), device, optimizer, lr=learningrate, monitor=monitor)

    elif model_type == 'agc':
        model = VGAEAGCEmb(data, dim, savepath)
        history = model.train(int(epochs), device, optimizer, lr=learningrate, monitor=monitor)

    elif model_type == 'node2vec' or model_type == 'n2v':
        print('Node2vec model havent been implemented yet, stop the training.')
        return 
        
    else:
        print('No matched mode type found')

    if not historypath is None and not history is None:
        print('-- Saving training history')
        with open(historypath, 'wb') as dt:
            pickle.dump(history, dt)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Training node embedding model for users')

    parser.add_argument('-t', '--type', default='vgae', help='type of model for node embedding')
    parser.add_argument('-dt', '--data', default='./files/normalized_graph_data_5.pt' ,help='torch_geometric Data')    
    parser.add_argument('-s', '--savepath', default=None, help='path to save model')
    parser.add_argument('-d', '--dim', default=128, help='embedding dimension')
    parser.add_argument('-gpu', '--gpu', default=False, help='using GPU')
    parser.add_argument('-e', '--epochs', default=5000)
    parser.add_argument('-optim', '--optimizer', default='adam')
    parser.add_argument('-lr', '--learningrate', default=0.001)
    parser.add_argument('-mnt', '--monitor', default='ap', help='metric to monitor')
    parser.add_argument('-hp', '--historypath', default=None)

    args = parser.parse_args()

    train(args.type, args.data, args.savepath, args.dim, args.gpu, args.epochs, args.optimizer, args.learningrate, args.monitor, args.historypath)

    # # setting device
    # if args.gpu is True:
    #     device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    #     if str(device) != 'cuda':
    #         print('GPU is not available, switch to CPU')
    #     else:
    #         print('GPU is activated')
    # else:
    #     device = torch.device('cpu')
    

    # print('Type of model: ', args.type)
    # history = None
    # if args.type == 'vgae':
    #     model = VGAEEmb(args.data, args.dim, args.savepath)
    #     history = model.train(int(args.epochs), device, args.optimizer, lr=args.learningrate, monitor=args.monitor)
    # elif args.type == 'gae':
    #     model = GAEEmb(args.data, args.dim, args.savepath)
    #     history = model.train(int(args.epochs), device, args.optimizer, lr=args.learningrate, monitor=args.monitor)
    # elif args.type == 'node2vec' or args.type == 'n2v':
    #     pass
    # else:
    #     print('No matched mode type found')

    # if not args.historypath is None and not history is None:
    #     print('-- Saving training history')
    #     with open(args.historypath, 'wb') as dt:
    #         pickle.dump(history, dt)

    

