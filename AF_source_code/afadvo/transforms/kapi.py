'''Transform function for Kapi DB'''

import numpy as np
import pandas as pd
import pickle
import sklearn

def group_post_by_user(df_post='../files/chosen_post_2.csv', save_path=None):
    r'''
    Read post.csv collection and return dictionary of user_id - post_ids
    
    Args:
        df_post: str or Pandas Dataframe. If str, df_post should be path to csv file
        save_path: path to save. If None, save process is skipped
    
    :rtype: python dictionary (user_post_dict: dictionary of user_id - post_ids)
    '''
    
    if type(df_post) is str:
        df_post = pd.read_csv(df_post, dtype={'fid': str, 'from_user': str, 'to_user': str, 'parent_id': str})
        
    user_post_dict = dict(df_post.drop(df_post.columns.difference(['from_user', 'fid']), 1, inplace=False).dropna().drop_duplicates().groupby('from_user')['fid'].apply(list))
    
    if not save_path is None:
        with open(save_path, 'wb') as dt:
            pickle.dump(user_post_dict, dt)
    
    return user_post_dict

def group_user_by_post(df_path, df_post, collection, save_path=None):
    r'''
    Read df.csv collection and return dictionary of post_id - user_ids
    
    Args:
        df_path: str. Path to DataFrame need to query (share, comment or react), df_path should be path to csv file
        df_post: str or Pandas Dataframe. DataFrame of chosen post. If str, df should be path to csv file
        collection: str, collection should be one of 'share', 'comment' or 'reaction'
        save_path: path to save. If None, save process is skipped

    :rtype: python dictionary
    '''
    
    if type(df_post) is str:
        df_post = pd.read_csv(df_post, dtype={'fid': str, 'from_user': str, 'to_user': str, 'parent_id': str})
        
    if collection == 'share':
        df = df.dropna(subset=['parent_id', 'from_user'])
        post_user_dict = dict(df.groupby('fid')['from_user'].apply(list))
        
    # Due to over size of comment and react, these csv file should be read in chunk
    elif collection == 'comment':
        # get all user ids who comments on those posts
        chunksize = 1e7
        post_ids = list(df_post.fid)
        cmt_user_ids = pd.DataFrame()
        for i,df in enumerate(pd.read_csv(df_path, dtype={'fid': str, 'post_id':str, 'from_user': str, 'to_user': str}, chunksize=chunksize)):
            df_temp = df[df.post_id.isin(post_ids)]
            cmt_user_ids = cmt_user_ids.append(df_temp, ignore_index=True)
            
        post_user_dict = dict(cmt_user_ids.drop(cmt_user_ids.columns.difference(['from_user','post_id']), 1, inplace=False).dropna().drop_duplicates().groupby('post_id')['from_user'].apply(list))
        
    elif collection == 'react' or collection == 'reaction':
        # get all user ids who comments on those posts
        chunksize = 1e7
        post_ids = list(df_post.fid)
        react_user_ids = pd.DataFrame()
        for i,df in enumerate(pd.read_csv(df_path, dtype={'fid': str, 'from_user_id': str}, chunksize=chunksize)):
            df_temp = df[df.fid.isin(post_ids)]
            react_user_ids = react_user_ids.append(df_temp, ignore_index=True)
            react_user_ids = react_user_ids.drop(react_user_ids.columns.difference(['fid','from_user_id']), 1, inplace=False).dropna().drop_duplicates()
        
        post_user_dict = dict(react_user_ids.dropna().drop_duplicates().groupby('fid')['from_user_id'].apply(list))
     
    if not save_path is None:
        with open(save_path, 'wb') as dt:
            pickle.dump(post_user_dict, dt)
            
    return post_user_dict

def generate_edge_list(user_post_dict='../files/group_post_by_user_in_post.hdf5', 
                       share_dict='../files/group_user_by_post_in_share.hdf5', 
                       comment_dict='../files/group_user_by_post_in_comment.hdf5', 
                       react_dict='../files/group_user_by_post_in_reaction.hdf5', 
                       save_path=None):
    
    r'''
    Generate edge list dictionary from dedicated dictionary of user_id - post_ids, and post_id - user_ids who share, comment and react
    
    Args:
        user_post_dict: str or python dict, user_id - post_ids dict. If str, it should be available path
        share_dict : user_id - post_ids who share
        comment_dict: user_id - post_ids who comment
        react_dict: user_id - post_ids who react
        save_path: str. If None, save process is skipped
    
    :rtype: python dictionary (user_edge_list)
    '''
    
    # load file
    
    if type(share_dict) is str:
        with open(share_dict, 'rb') as dt:
            share_dict = pickle.load(dt)

    if type(user_post_dict) is str:
        with open(user_post_dict, 'rb') as dt:
            user_post_dict = pickle.load(dt)

    if type(comment_dict) is str:
        with open(comment_dict, 'rb') as dt:
            comment_dict = pickle.load(dt)

    if type(react_dict) is str:
        with open(react_dict, 'rb') as dt:
            react_dict = pickle.load(dt)
            
    print('- user_post_dict records: ', len(user_post_dict))
    print('- share_dict records: ', len(share_dict))
    print('- comment_dict records: ', len(comment_dict))
    print('- react_dict records: ', len(react_dict))
    
            
    user_edge_list = {}
    counter = 0
    n = 0
    for k,v in user_post_dict.items():

        for pid in v:
            # share
            if pid in share_dict:
                # user id is first part of '_' in parent_id
                _share = [str(k) for k in share_dict[pid]]
            else:
                _share = []

            # comment
            if pid in comment_dict:
                _comment = [str(k) for k in comment_dict[pid]]
            else:
                _comment = []

            # reaction
            if pid in react_dict:
                _react = [str(k) for k in react_dict[pid]]
            else:
                _react = []

            # concat list
            n += 1
            if len(_share) == 0 and len(_comment) == 0 and len(_react) == 0:
                counter += 1
            else:
                uids = np.unique(np.array(_share + _comment + _react, dtype=str))
                idx = np.where(uids == str(k))[0]
                
                if len(idx) > 0:
                    uids = np.delete(uids, idx)
                    
                    if len(uids) == 0:
                        continue
                
                user_edge_list[str(k)] = uids
                
    print('- Number of isolated nodes: ', counter, ' | Percentage: ', (counter/n)*100)
    
    return user_edge_list

def count_by_user(df_path, collection, device,
                  user_edge_list='../files/user_edge_list_3.hdf5', 
                  user_post_dict='../files/group_post_by_user_in_post.hdf5',
                  chunksize=1e7,
                  save_path=None):
    r'''
    Counter number of shares, comments or reactions by user
    
    Args:
        df_path: path to concerned Pandas Dataframe
        user_edge_list: str or DataFrame. if str, it should be available path
        user_post_dict: str or dictionary
        collections: str. one of 'share', 'comment' or 'react'
    
    :rtype: python dictionary, (number of shares/comments/reacts by user_id)
    '''
    
    if type(user_edge_list) is str:
        with open(user_edge_list, 'rb') as dt:
            user_edge_list = pickle.load(dt)
    
    if type(user_post_dict) is str:
        with open(user_post_dict, 'rb') as dt:
            user_post_dict = pickle.load(dt)
    
    edge_count = {}
    n_counter = 0
    
    if collection == 'share':
        edge_count = count_by_user_share(df_path, device, user_edge_list, user_post_dict, chunksize)
    elif collection == 'comment':
        edge_count = count_by_user_comment(df_path, device, user_edge_list, user_post_dict, chunksize)
    elif collection == 'react' or collection == 'reaction':
        edge_count = count_by_user_react(df_path, device, user_edge_list, user_post_dict, chunksize)

    if not save_path is None:
        with open(save_path, 'wb') as dt:
            pickle.dump(edge_count, dt)
            
    return edge_count
                          

def count_by_user_share(df_path, device,
                  user_edge_list='../files/user_edge_list_3.hdf5', 
                  user_post_dict='../files/group_post_by_user_in_post.hdf5',
                  chunksize=10000):
    if type(user_edge_list) is str:
        with open(user_edge_list, 'rb') as dt:
            user_edge_list = pickle.load(dt)
    
    if type(user_post_dict) is str:
        with open(user_post_dict, 'rb') as dt:
            user_post_dict = pickle.load(dt)
    
    edge_count = {}
                          
    for i,df in enumerate(pd.read_csv(df_path, dtype = {'fid':str, 'from_user':str, 'parent_id': str}, chunksize=chunksize)):
        for k,v in user_edge_list.items():
                          
            pids = user_post_dict[int(k)]
            _dict = dict(df[df.from_user.isin(v) & df.parent_id.isin(pids)].groupby('from_user')['fid'].count())

            if not k in edge_count:
                edge_count[k] = np.zeros(len(v), dtype=int)
            else:
                n_counts = edge_count[k]
                for u,j in _dict.items():
                    idx = np.where(v == str(u))[0][0]
                    n_counts[idx] = j

                edge_count[k] = n_counts
                          
    return edge_count
                          
def count_by_user_comment(df_path, device,
                  user_edge_list='../files/user_edge_list_3.hdf5', 
                  user_post_dict='../files/group_post_by_user_in_post.hdf5',
                  chunksize=10000):
    if type(user_edge_list) is str:
        with open(user_edge_list, 'rb') as dt:
            user_edge_list = pickle.load(dt)
    
    if type(user_post_dict) is str:
        with open(user_post_dict, 'rb') as dt:
            user_post_dict = pickle.load(dt)
    
    edge_count = {}
                          
    for i,df in enumerate(pd.read_csv(df_path, dtype = {'fid': str, 'post_id':str, 'from_user': str, 'to_user': str}, 
                                      chunksize=chunksize)):
        for k,v in user_edge_list.items():
                          
            pids = user_post_dict[int(k)]
            _dict = dict(df[df.from_user.isin(v) & df.post_id.isin(pids)].groupby('from_user')['post_id'].count())

            if not k in edge_count:
                edge_count[k] = np.zeros(len(v), dtype=int)
            else:
                n_counts = edge_count[k]
                for u,j in _dict.items():
                    idx = np.where(v == str(u))[0][0]
                    n_counts[idx] = j

                edge_count[k] = n_counts
                          
    return edge_count
                          
def count_by_user_react(df_path, device,
                  user_edge_list='../files/user_edge_list_3.hdf5', 
                  user_post_dict='../files/group_post_by_user_in_post.hdf5',
                  chunksize=1e7):
    if type(user_edge_list) is str:
        with open(user_edge_list, 'rb') as dt:
            user_edge_list = pickle.load(dt)
    
    if type(user_post_dict) is str:
        with open(user_post_dict, 'rb') as dt:
            user_post_dict = pickle.load(dt)
    
    edge_count = {}
                          
    for i,df in enumerate(pd.read_csv(df_path, dtype = {'fid': str, 'from_user_id': str}, 
                                      chunksize=chunksize)):
        for k,v in user_edge_list.items():
                          
            pids = user_post_dict[int(k)]
            _dict = dict(df[df.from_user_id.isin(v) & df.fid.isin(pids)].groupby('from_user_id')['fid'].count())

            if not k in edge_count:
                edge_count[k] = np.zeros(len(v), dtype=int)
            else:
                n_counts = edge_count[k]
                for u,j in _dict.items():
                    idx = np.where(v == str(u))[0][0]
                    n_counts[idx] = j

                edge_count[k] = n_counts
                          
    return edge_count


def generate_edge_attribute(edge_list = ['../files/edge_share_3.hdf5', 
                                         '../files/edge_comment_3.hdf5', 
                                         '../files/edge_react_3.hdf5'], 
                            save_path=None):
    r'''
    Generate edge attribute from list of edges
    
    Args:
        edge_list: [str] or [dictionary]. List of edge attribute count
        save_path: str or None.

    :rtype: python dictionary (feature edge dictionary)
    '''
    
    if not type(edge_list) is list or not type(edge_list) is np.ndarray:
        edge_list = np.asarray(edge_list)
        
    print(edge_list)
    
    edge_attrs = []
    for path in edge_list:
        with open(path, 'rb') as dt:
            temp = pickle.load(dt)
            print(temp)
            edge_attrs.append(temp)
            print(edge_attrs)


    edge_feature = {}
    
    for k,v in edge_attrs[0].items():
        atts = []
        for i in range(len(v)):
            _att = np.asarray([d[k][i] for d in edge_attrs], dtype=int)
            atts.append(_att)
        
        edge_feature[k] = atts
    
    if not save_path is None:
        with open(save_path, 'wb') as dt:
            pickle.dump(edge_feature, dt)
    
    return edge_feature

def generate_node_attribute(user_edge_list='../files/user_edge_list_3.hdf5', 
                           df_user='../files/chosen_users.csv',
                           attrs=['total_follower', 'total_friend', 'books_count', 'films_count', 'music_count', 'restaurants_count', 'sex'], 
                           save_path=None):
    r'''
    Generate node attributes by given list
    
    Args:
        user_edge_list: str or dict python. If str, it should be path
        df_user: str or DataFrame, user dataframe
        attrs: list, name of concerned attributes from df_user
        save_path: str or None. If None, save process is skipped

    :rtype: python dictionary (node_atts_list: dict, key is node_id, values is array of concerned attributes)
    '''
    
    if type(user_edge_list) is str:
        with open(user_edge_list, 'rb') as dt:
            user_edge_list = pickle.load(dt)
            
    if type(df_user) is str:
        df_user = pd.read_csv(df_user, dtype={'fid': str})
        
    # get all distinct uids
    unique_uid_keys = np.unique(list(user_edge_list.keys()))
    unique_uid_values = np.unique(np.concatenate(list(user_edge_list.values())))
    uids = np.unique(np.concatenate([unique_uid_keys, unique_uid_values]))
    
    # filtered in df_user
    df_filtered_user = df_user[df_user.fid.isin(uids)]
    
    # fill na data, all are 0.0 as default excepts sex is 3.0
#     fill_data = {'total_follower': 0.0, 'total_friend': 0.0, 'books_count': 0.0, 'films_count': 0.0, 'music_count': 0.0, 'restaurants_count': 0.0}
#     for att in attrs:
#         if att == 'sex':
#             fill_data[att] = 3.0
#         else:
#             fill_data[att] = 0.0
            
    if 'sex' in attrs:
        df_filtered_user.sex = df_filtered_user.sex.map({3.0:3.0, 'Nam': 0.0, 'Nữ': 1.0, 'Gay': 2.0, 'Mộc Nhiên': 1.0})
    
    for att in attrs:
        imputer = sklearn.impute.SimpleImputer(missing_values=np.nan, strategy='mean')
        imputer = imputer.fit(df_filtered_user[[att]])
        df_filtered_user[att] = imputer.transform(df_filtered_user[[att]])
    
    
    attrs += ['fid']
    print(attrs)
#     df_filtered_user = df_filtered_user.fillna(value=fill_data).drop(df_filtered_user.columns.difference(attrs), 1, inplace=False)
    df_filtered_user = df_filtered_user.drop(df_filtered_user.columns.difference(attrs), 1, inplace=False)
    
    
        
    # create node_atts_list dictionary
    values_att = df_filtered_user.drop('fid', axis=1).values
    key_att = list(df_filtered_user['fid'])
    node_atts = dict(zip(key_att, values_att))
    
    if not save_path is None:
        with open(save_path, 'wb') as dt:
            pickle.dump(node_atts, dt)
    
    return node_atts
    
    