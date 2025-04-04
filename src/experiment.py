import time
import tracemalloc
import numpy as np
import utils
import suffix_trie
import suffix_tree
import suffix_array
import sys
import argparse
import matplotlib.pyplot as plt
import pandas as pd

# Function to measure memory usage
def get_memory_usage(obj):
    tracemalloc.start()
    _ = obj  # Force object reference
    mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return mem[1] - mem[0]

def get_args():
    parser = argparse.ArgumentParser(description='Suffix Indexing Experiment')
    
    parser.add_argument('--seq_length', nargs='+', type=int, default=[10000, 50000, 100000],
                        help='List of sequence lengths to test')
    parser.add_argument('--query_length', nargs='+', type=int, default=[5, 10, 20],
                        help='List of query lengths to test')
    
    return parser.parse_args()

def run_test(test_function, T, P):
    """Runs a test function and measures runtime + memory usage"""
    start = time.monotonic_ns()
    _ = test_function(T, P)
    stop = time.monotonic_ns()

    tracemalloc.start()
    _ = test_function(T, P)
    mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return (stop - start) / 1e9, mem[1] - mem[0]  # Convert ns to seconds

def test_harness(test_functions, text_sizes, pattern_size, rounds):
    """Runs tests on multiple functions, collecting runtime & memory usage"""
    run_times = [[] for _ in range(len(test_functions))]
    mem_usages = [[] for _ in range(len(test_functions))]
    query_times = [[] for _ in range(len(test_functions))]

    for text_size in text_sizes:
        print(f"\nProcessing sequence length {text_size}...")
        _run_times = [[] for _ in range(len(test_functions))]
        _mem_usages = [[] for _ in range(len(test_functions))]
        _query_times = [[] for _ in range(len(test_functions))]

        for _ in range(rounds):
            T = ''.join(utils.sim_reads('ACGT' * (text_size // 4), text_size, 1, 0))
            P = T[:pattern_size]  

            for j, test_function in enumerate(test_functions):
                print(f"    Running {['Trie', 'Tree', 'Array'][j]}...")
                run_time, mem_usage = run_test(test_function, T, P)
                _run_times[j].append(run_time)
                _mem_usages[j].append(mem_usage)
                _query_times[j].append(run_time)

        for j in range(len(test_functions)):
            run_times[j].append(np.mean(_run_times[j]))
            mem_usages[j].append(np.mean(_mem_usages[j]))
            query_times[j].append(np.mean(_query_times[j]))

    return run_times, mem_usages, query_times

def run_experiment():
    text_sizes = [5000, 20000, 50000]
    pattern_size = 10
    rounds = 1

    test_functions = [
        lambda T, P: suffix_trie.search_trie(suffix_trie.build_suffix_trie(T), P),
        lambda T, P: suffix_tree.search_tree(suffix_tree.build_suffix_tree(T), P),
        lambda T, P: suffix_array.search_array(T, suffix_array.build_suffix_array(T), P),
    ]

    run_times, mem_usages, query_times = test_harness(test_functions, text_sizes, pattern_size, rounds)

    results = []
    for i, name in enumerate(["Trie", "Tree", "Array"]):
        for j, size in enumerate(text_sizes):
            results.append((name, size, run_times[i][j], mem_usages[i][j], query_times[i][j]))
    
    plot_results(results)

def plot_results(results):
    df = pd.DataFrame(results, columns=["Data Structure", "Sequence Length", "Build Time (s)", "Memory Usage (bytes)", "Query Time (s)"])
    
    #build times
    plt.figure(figsize=(10, 5))
    for structure in df["Data Structure"].unique():
        subset = df[df["Data Structure"] == structure]
        plt.plot(subset["Sequence Length"], subset["Build Time (s)"], marker='o', label=f"{structure} Build Time")
    plt.xlabel("Sequence Length")
    plt.ylabel("Build Time (s)")
    plt.title("Build Time vs Sequence Length")
    plt.legend()
    plt.grid()
    plt.savefig("build_time.png")
    plt.close()
    
    #memory usage
    plt.figure(figsize=(10, 5))
    for structure in df["Data Structure"].unique():
        subset = df[df["Data Structure"] == structure]
        plt.plot(subset["Sequence Length"], subset["Memory Usage (bytes)"], marker='o', label=f"{structure} Memory Usage")
    plt.xlabel("Sequence Length")
    plt.ylabel("Memory Usage (bytes)")
    plt.title("Memory Usage vs Sequence Length")
    plt.legend()
    plt.grid()
    plt.savefig("memory_usage.png")
    plt.close()

    #query time
    plt.figure(figsize=(10, 5))
    for structure in df["Data Structure"].unique():
        subset = df[df["Data Structure"] == structure]
        plt.plot(subset["Sequence Length"], subset["Query Time (s)"], marker='o', label=f"{structure} Query Time")
    plt.xlabel("Sequence Length")
    plt.ylabel("Query Time (s)")
    plt.title("Query Time vs Sequence Length")
    plt.legend()
    plt.grid()
    plt.savefig("query_time.png")
    plt.close()

if __name__ == "__main__":
    args = get_args()
    run_experiment()
