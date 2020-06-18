import pickle
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE


def visualize_tsne(z, n_dim=2, figsize=(150,150), save_emb_path=None, save_fig_path=None):
    '''
        Visualize vector space by given alogrithm
        '''
    embs = TSNE(n_components=n_dim).fit_transform(z.cpu().detach().numpy())

    with not save_emb_path is None:
        with open(save_emb_path, 'wb') as dt:
            pickle.dump(embs, dt)

    # visualize
    plt.figure(figsize=figsize)
    plt.scatter(embs[:, 0], embs[:, 1], s=20)

    if not save_fig_path is None:
        plt.savefig(save_fig_path)

    plt.show()
    
