'''Calculation AF score'''

import argparse
from utils.predict import get_similarity_2, cal_af_2 
import pickle

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate AF from given node embedding')
    parser.add_argument('-uid', '--uid', help='user id')
    parser.add_argument('-el', '--edgelist', default='./files/user_edge_list_3.hdf5', help='user edge list file store the interaction among users or can be path')
    parser.add_argument('-emb', '--embedding', default='./files/nVGAE4_128_emb_cpu.hdf5', help='embedding vector or can be path to file')
    parser.add_argument('-ndict', '--nodedict', default='./files/node_dict_4.hdf5', help='node dictionary mapping uids into orders, or can be path')
    parser.add_argument('-th', '--threshold', default=0.5, help='threshold to confirm influence (0 to 1)')
    parser.add_argument('-lm', '--limit', default=100, help='limit tracking level ')

    args = parser.parse_args()

    uid = args.uid
    edge_list = args.edgelist
    z = args.embedding
    node_dict = args.nodedict
    threshold = args.threshold
    limit = args.limit

    if not type(uid) is str:
        uid = str(uid)

    if type(edge_list) is str:
        with open(edge_list, 'rb') as dt:
            edge_list = pickle.load(dt)

    if type(z) is str:
        with open(z, 'rb') as dt:
            z = pickle.load(dt)
    print(z)
    # z = z.cpu().detach().numpy()

    if type(node_dict) is str:
        with open(node_dict, 'rb') as dt:
            node_dict = pickle.load(dt)

    

    dirs, probs, degs = get_similarity_2(uid, edge_list, z, node_dict, threshold, limit)
    af_score = cal_af_2(uid, dirs, probs, degs)

    print(uid, ' : ', af_score)
