import argparse
import utils
import suffix_tree

SUB = 0
CHILDREN = 1

def get_args():
    parser = argparse.ArgumentParser(description='Suffix Tree')

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

def build_suffix_array(T):
    tree = suffix_tree.build_suffix_tree(T)
    suffix_array = []

    # Perform depth-first traversal
    stack = [0]
    suffixes = []

    while stack:
        node_idx = stack.pop()
        node = tree[node_idx]

        if not node[CHILDREN]:  # Leaf node
            suffix_start = len(T) - len(node[SUB])
            suffixes.append((T[suffix_start:], suffix_start))  # Store (suffix, index)

        for child in sorted(node[CHILDREN].values(), reverse=True):
            stack.append(child)

    # Sort by lexicographic order of suffixes
    suffix_array = [suffix[1] for suffix in sorted(suffixes)]

    # Debugging print
    print("\nBuilt suffix array:")
    for suffix in suffix_array[:10]:  # Print first 10 entries
        print(f"   {suffix}: {T[suffix:]}")

    return suffix_array



def search_array(T, suffix_array, q):
    if not suffix_array:  
        print("ERROR: Suffix array is empty!")
        return 0

    print(f"Searching for: {q} in suffix array of size {len(suffix_array)}")

    lo, hi = 0, len(suffix_array) - 1  # Adjusted lo and hi bounds
    while lo <= hi:
        mid = (lo + hi) // 2
        suffix = T[suffix_array[mid]:]  

        print(f"  ▶ Binary search: lo={lo}, hi={hi}, mid={mid}, suffix='{suffix[:10]}...'")

        if suffix.startswith(q):
            print(f"Match found at index {suffix_array[mid]}")
            return len(q)  # Match found!
        elif suffix < q:
            lo = mid + 1
        else:
            hi = mid - 1

    print("No match found.")
    return 0



def main():
    args = get_args()

    T = None

    if args.string:
        T = args.string
    elif args.reference:
        reference = utils.read_fasta(args.reference)
        T = reference[0][1]

    array = build_suffix_array(T)

    if args.query:
        for query in args.query:
            match_len = search_array(array, query)
            print(f'{query} : {match_len}')

if __name__ == '__main__':
    main()
