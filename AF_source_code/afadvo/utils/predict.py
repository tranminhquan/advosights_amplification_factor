import numpy as np
import sklearn

def get_similarity_2(uid, edge_list, z, node_dict, threshold=0.5, limit=100):
    stack = []
    
    af_directions = {}
    af_probs = {}           
    af_degs = {}
    
    stack.append(str(uid))
    counter = 0
    while len(stack) > 0 and counter < limit:
        counter += 1
#         print('stack: ', stack)
        node = stack.pop()
        
        if str(node) in stack:
            print('***********', node, '************')
            
        # look-up in user_edge_list
        try:
            uids = edge_list[str(node)]
        except KeyError:
            print('- Key ', node, ' finished')
            continue
        
        # cal similarity
        if len(uids) == 0:
            continue

        if len(uids) == 1 and node == uids[0]:
            continue

        # if node not in uids
        index = np.where(uids == str(node))[0]
        if len(index) == 0:
            t = np.concatenate([np.array([node]), uids])
        else:
            index = index[0]
            t = np.concatenate([np.array([uids[index]]), uids[:index], uids[index+1:]])

        atts = np.array([np.array(z[node_dict[int(k)], :]) for k in t])
        sims = sklearn.metrics.pairwise.cosine_similarity(atts)[0,:]
        
        edge_list = []
        edge_prob = []
        edge_outdeg = []
        for i in range(1, len(t)):
            if sims[i] > threshold:
                
                edge_list.append(t[i])
                edge_prob.append(sims[i])
                if not str(t[i]) in edge_list:
                    edge_outdeg.append(1)
                    print('- End at ', str(t[i]))
                else:
                    edge_outdeg.append(len(edge_list[str(t[i])]))
                    # ADD TO STACK
                    stack.append(str(t[i]))
                    
                
        af_directions[node] = edge_list
        af_probs[node] = edge_prob
        af_degs[node] = edge_outdeg
        
        print(af_directions)
    
    return af_directions, af_probs, af_degs


def cal_af_2(uid, af_directions, af_probs, af_degs):
    af_score = 0.0
    
    for i, (k,v) in enumerate(af_directions.items()):
        for j in range(len(v)):
            af_score += (af_probs[k][j] * af_degs[k][j])
    return af_score