import argparse
from afadvo.utils.predict import get_similarity_2, cal_af_2

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate AF from given node embedding')
    parser.add_argument('-uid', '--uid', help='user id')
    parser.add_argument('-el', '--edgelist', help='user edge list file store the interaction among users or can be path')
    parser.add_argument('-emb', '--embedding', help='embedding vector or can be path to file')
    parser.add_argument('-ndict', '--nodedict', help='node dictionary mapping uids into orders, or can be path')
    parser.add_argument('-th', '--threshold', help='threshold to confirm influence (0 to 1)')
    parser.add_argument('-lm', '--limit', help='limit tracking level ')

    dirs, probs, degs = get_similarity_2()

    args = my_parser.parse_args()