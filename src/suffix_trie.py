import argparse
import utils

class SuffixTrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

def get_args():
    parser = argparse.ArgumentParser(description='Suffix Trie')

    parser.add_argument('--reference',
                        help='Reference sequence file',
                        type=str)

    parser.add_argument('--string',
                        help='Reference sequence',
                        type=str)

    parser.add_argument('--query',
                        help='Query sequences',
                        nargs='+',
                        type=str)

    return parser.parse_args()

def build_suffix_trie(s):
    root = SuffixTrieNode()
    for i in range(len(s)):
        node = root
        for char in s[i:]:
            if char not in node.children:
                node.children[char] = SuffixTrieNode()
            node = node.children[char]
        node.is_end = True
    return root

def search_trie(trie, pattern):
    node = trie
    match_length = 0
    for char in pattern:
        if char in node.children:
            node = node.children[char]
            match_length += 1
        else:
            break
    return match_length

def main():
    args = get_args()

    T = None

    if args.string:
        T = args.string
    elif args.reference:
        reference = utils.read_fasta(args.reference)
        T = reference[0][1]

    trie = build_suffix_trie(T)

    if args.query:
        for query in args.query:
            match_len = search_trie(trie, query)
            print(f'{query} : {match_len}')

if __name__ == '__main__':
    main()
