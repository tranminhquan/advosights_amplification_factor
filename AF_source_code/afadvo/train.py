'''Training embedding model (phase 1)'''
import argparse
import torch
from nn.models.vgae import VGAEEmb
from nn.models.node2vec import Node2VecEmb

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

    # setting device
    if args.gpu is True:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if str(device) != 'cuda':
            print('GPU is not available, switch to CPU')
        else:
            print('GPU is activated')
    else:
        device = torch.device('cpu')
    

    print('Type of model: ', args.type)
    if args.type == 'vgae':
        model = VGAEEmb(args.data, args.dim, args.savepath)
        history = model.train(int(args.epochs), device, args.optimizer, lr=args.learningrate, monitor=args.monitor)
    elif args.type == 'gae':
        pass
    elif args.type == 'node2vec' or args.type == 'n2v':
        pass
    else:
        print('No matched mode type found')

