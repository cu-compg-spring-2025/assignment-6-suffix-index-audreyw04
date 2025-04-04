import tracemalloc
import time
import numpy as np
import random
import argparse
import matplotlib.pyplot as plt
import utils
import suffix_trie
import suffix_tree
import suffix_array

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--text_range',
                        type=int,
                        required=True,
                        nargs=3,
                        help='Text size parameters (start stop step)')
    parser.add_argument('--pattern_size',
                        type=int,
                        required=True,
                        help='Pattern size')
    parser.add_argument('--rounds',
                        type=int,
                        default=10,
                        help='Number of rounds to run each algorithm ' \
                             + '(default: 10)')
    return parser.parse_args()

def get_random_string(alphabet, length):
    return ''.join(random.choice(alphabet) for _ in range(length))

def get_random_substring(string, length):
    if length > len(string):
        raise ValueError("Length of substring is longer than the string.")
    start_index = random.randint(0, len(string) - length)
    return string[start_index:start_index + length]

def run_test(test_function, T, P):
    start = time.monotonic_ns()
    r = test_function(T, P)
    stop = time.monotonic_ns()

    tracemalloc.start()
    r = test_function(T, P)
    mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return stop - start, mem[1] - mem[0]

def test_harness(test_functions, text_size_range, pattern_size, rounds):
    run_times = [[] for _ in range(len(test_functions))]
    mem_usages = [[] for _ in range(len(test_functions))]

    for text_size in text_size_range:
        print(f"\nTesting sequence size: {text_size}")  # Debug print
        _run_times = [[] for _ in range(len(test_functions))]
        _mem_usages = [[] for _ in range(len(test_functions))]

        for _ in range(rounds):
            T = get_random_string(['A', 'C', 'T', 'G'], text_size)
            P = get_random_substring(T, pattern_size)

            for j, test_function in enumerate(test_functions):
                print(f"  Running {['Trie', 'Tree', 'Array'][j]}...")  # Debug print
                try:
                    run_time, mem_usage = run_test(test_function, T, P)
                    _run_times[j].append(run_time)
                    _mem_usages[j].append(mem_usage)
                except Exception as e:
                    print(f"ERROR in {['Trie', 'Tree', 'Array'][j]}: {e}")  # Catch errors

        for j in range(len(test_functions)):
            run_times[j].append(np.mean(_run_times[j]) if _run_times[j] else 0)
            mem_usages[j].append(np.mean(_mem_usages[j]) if _mem_usages[j] else 0)

    return run_times, mem_usages

def main():
    args = get_args()
    text_size_range = range(args.text_range[0], args.text_range[1], args.text_range[2])
    pattern_size = args.pattern_size
    rounds = args.rounds
    
    test_functions = [
        lambda T, P: suffix_trie.search_trie(suffix_trie.build_suffix_trie(T), P),
        lambda T, P: suffix_tree.search_tree(suffix_tree.build_suffix_tree(T), P),
        lambda T, P: suffix_array.search_array(T, suffix_array.build_suffix_array(T), P)
    ]
    
    run_times, mem_usages = test_harness(test_functions, text_size_range, pattern_size, rounds)

    line_styles = ['solid', 'dashed', 'dotted']  # Different styles for Trie, Tree, Array

    fig, axs = plt.subplots(2, 1)
    fig.tight_layout(pad=3.0)

    ax = axs[0]
    for i, (label, style) in enumerate(zip(['Trie', 'Tree', 'Array'], line_styles)):
        ax.plot(text_size_range, run_times[i], linestyle=style, marker='o', label=label)
    ax.set_title(f'Suffix Indexing Performance (|P|= {pattern_size})')
    ax.set_xlabel('Text size')
    ax.set_ylabel('Run time (ns)')
    ax.legend(loc='best', frameon=False, ncol=3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax = axs[1]
    for i, (label, style) in enumerate(zip(['Trie', 'Tree', 'Array'], line_styles)):
        ax.plot(text_size_range, mem_usages[i], linestyle=style, marker='o', label=label)
    ax.set_xlabel('Text size')
    ax.set_ylabel('Memory (bytes)')
    ax.legend(loc='best', frameon=False, ncol=3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.savefig("runtime_plot.png")
    plt.close()

    plt.figure()
    for i, (label, style) in enumerate(zip(['Trie', 'Tree', 'Array'], line_styles)):
        plt.plot(text_size_range, mem_usages[i], linestyle=style, marker='o', label=label)
    plt.xlabel('Text size')
    plt.ylabel('Memory (bytes)')
    plt.title('Memory Usage vs Text Size')
    plt.legend(loc='best', frameon=False, ncol=3)
    plt.grid()
    plt.savefig("memory_usage_plot.png")
    plt.close()

    T = "ACGTACGTACGT"
    P = "ACGT"

    print("Building Tree...")
    tree = suffix_tree.build_suffix_tree(T)
    print("Searching Tree...")
    print(suffix_tree.search_tree(tree, P))

    print("Building Array...")
    array = suffix_array.build_suffix_array(T)
    print("Searching Array...")
    print(suffix_array.search_array(T, array, P))

if __name__ == '__main__':
    main()