import argparse
import time
import pickle
import torch
from transforms.kapi import *
import warnings

# Ignore warnings
warnings.filterwarnings("ignore")

def transform_kapi_data(database, users, posts, comments, reactions, edgelist, nodeattr, edgeattr, torchdata):
    # EDGE LIST
    print('- Creating user edge list . . .')
    start_edge_list = time.time()

    user_post_dict = group_post_by_user(df_post=posts, save_path=None)
    
    post_share = group_user_by_post(df_path=posts, df_post=posts, collection='share', save_path=None)
    post_comment = group_user_by_post(df_path=comments, df_post=posts, collection='comment', save_path=None) if not comments is None else None
    post_react = group_user_by_post(df_path=reactions, df_post=posts, collection='react', save_path=None) if not reactions is None else None

    edge_list = generate_edge_list(user_post_dict=user_post_dict, share_dict=post_share, comment_dict=post_comment, react_dict=post_react, save_path=None)
    
    if not edgelist is None:
        with open(edgelist, 'wb') as dt:
            pickle.dump(edge_list, dt)

    print('* Edge list done: ', time.time() - start_edge_list)

    # NODE ATTRIBUTE
    print('- Creating node attribute . . .')
    start_nodeattr = time.time()
    node_attr = generate_node_attribute(user_edge_list=edge_list, df_user=users, save_path=nodeattr)
    print('* Node attribute done: ', time.time() - start_nodeattr)

    # EDGE ATTRIBUTE
    print('- Creating edge attribute . . .')
    start_edgeattr = time.time()
    share_count = count_by_user(df_path=posts, collection='share', user_edge_list=edge_list, user_post_dict=user_post_dict)
    comment_count = count_by_user(df_path=comments, collection='comment', user_edge_list=edge_list, user_post_dict=user_post_dict)
    react_count = count_by_user(df_path=reactions, collection='react', user_edge_list=edge_list, user_post_dict=user_post_dict)

    edge_attr = generate_edge_attribute(edge_list=[share_count, comment_count, react_count], save_path=edgeattr)
    print('* Edge list done: ', time.time() - start_edgeattr)

    # GENERATE TORCH-GEO DATA INSTANCE
    print('- Creating torch-geometric data . . .')
    start_torchgeodata = time.time()
    torch_data = generate_data_torchgeo(edge_list=edge_list, node_atts=node_attr, edge_atts=edge_attr, reindex=True, save_path=torchdata)
    print('* Torch-geo data done: ', time.time() - start_torchgeodata)

    return torch_data

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Tranform from raw MongoDB data to knowledge graph data')
    
    parser.add_argument('-db', '--database', default='kapi', help='type of database')
    parser.add_argument('-users', '--users', default='/tf/data/adv/node_embedding/chosen_users_2.csv' ,help='path to user csv file')
    parser.add_argument('-posts', '--posts', default='/tf/data/adv/node_embedding/chosen_post_2.csv' ,help='path to posts csv file')
    parser.add_argument('-comments', '--comments', default='/tf/data/adv/node_embedding/chosen_comment.csv' ,help='path to user comments file')
    parser.add_argument('-reactions', '--reactions', default='/tf/data/adv/node_embedding/chosen_react.csv' ,help='path to user reactions file')

    parser.add_argument('-edgelist', '--edgelist', default=None, help='path to save edge list')
    parser.add_argument('-nodeattr', '--nodeattr', default=None, help='path to save node attribute')
    parser.add_argument('-edgeattr', '--edgeattr', default=None, help='path to save edge attribute')
    parser.add_argument('-torchdata', '--torchdata', default=None, help='path to save torch-geo data instance')

    args = parser.parse_args()

    torch_data = transform_kapi_data(args.database, args.users, args.posts, args.comments, args.reactions, args.edgelist, args.nodeattr, args.edgeattr, args.torchdata)

    # # EDGE LIST
    # print('- Creating user edge list . . .')
    # start_edge_list = time.time()

    # user_post_dict = group_post_by_user(df_post=args.posts, save_path=None)
    
    # post_share = group_user_by_post(df_path=args.posts, df_post=args.posts, collection='share', save_path=None)
    # post_comment = group_user_by_post(df_path=args.comments, df_post=args.posts, collection='comment', save_path=None) if not args.comments is None else None
    # post_react = group_user_by_post(df_path=args.reactions, df_post=args.posts, collection='react', save_path=None) if not args.reactions is None else None

    # edge_list = generate_edge_list(user_post_dict=user_post_dict, share_dict=post_share, comment_dict=post_comment, react_dict=post_react, save_path=None)
    
    # if not args.edgelist is None:
    #     with open(args.edgelist, 'wb') as dt:
    #         pickle.dump(edge_list, dt)

    # print('* Edge list done: ', time.time() - start_edge_list)

    # # NODE ATTRIBUTE
    # print('- Creating node attribute . . .')
    # start_nodeattr = time.time()
    # node_attr = generate_node_attribute(user_edge_list=edge_list, df_user=args.users, save_path=args.nodeattr)
    # print('* Node attribute done: ', time.time() - start_nodeattr)

    # # EDGE ATTRIBUTE
    # print('- Creating edge attribute . . .')
    # start_edgeattr = time.time()
    # share_count = count_by_user(df_path=args.posts, collection='share', user_edge_list=edge_list, user_post_dict=user_post_dict)
    # comment_count = count_by_user(df_path=args.comments, collection='comment', user_edge_list=edge_list, user_post_dict=user_post_dict)
    # react_count = count_by_user(df_path=args.reactions, collection='react', user_edge_list=edge_list, user_post_dict=user_post_dict)

    # edge_attr = generate_edge_attribute(edge_list=[share_count, comment_count, react_count], save_path=args.edgeattr)
    # print('* Edge list done: ', time.time() - start_edgeattr)

    # # GENERATE TORCH-GEO DATA INSTANCE
    # print('- Creating torch-geometric data . . .')
    # start_torchgeodata = time.time()
    # torch_data = generate_data_torchgeo(edge_list=edge_list, node_atts=node_attr, edge_atts=edge_attr, reindex=True, save_path=args.torchdata)
    # print('* Torch-geo data done: ', time.time() - start_torchgeodata)