import osmnx as ox
import random
from search_algorithms import greedy_best_first_search, astar_search

# Load saved graphs from disk (no re-downloading!)
print("Loading graphs...")
baku = ox.load_graphml("graphs/baku.graphml")
tbilisi = ox.load_graphml("graphs/tbilisi.graphml")
print("Loaded! ✅\n")

def run_experiment(graph, city_name, num_pairs=100):

    print(f"{'='*50}")
    print(f"  {city_name}")
    print(f"{'='*50}")

    nodes = list(graph.nodes)
    results = []

    for i in range(num_pairs):
        # Pick random start and goal nodes
        start, goal = random.sample(nodes, 2)

        print(f"\nPair {i+1}: {start} → {goal}")

        # Run Greedy
        greedy = greedy_best_first_search(graph, start, goal)
        # Run A*
        astar  = astar_search(graph, start, goal)

        if greedy['found'] and astar['found']:
            length_diff = greedy['path_length'] - astar['path_length']
            expanded_diff = greedy['nodes_expanded'] - astar['nodes_expanded']

            print(f"  Greedy → nodes expanded: {greedy['nodes_expanded']:,}  |  path length: {greedy['path_length']:,.1f}m")
            print(f"  A*     → nodes expanded: {astar['nodes_expanded']:,}  |  path length: {astar['path_length']:,.1f}m")
            print(f"  → A* expanded {abs(expanded_diff):,} {'more' if expanded_diff < 0 else 'fewer'} nodes")
            print(f"  → Greedy path is {length_diff:,.1f}m {'longer' if length_diff > 0 else 'shorter'} than A*")

            results.append({
                'city': city_name,
                'greedy_expanded': greedy['nodes_expanded'],
                'astar_expanded': astar['nodes_expanded'],
                'greedy_length': greedy['path_length'],
                'astar_length': astar['path_length'],
            })
        else:
            print(f"  One or both algorithms did not find a path — skipping pair.")

    # Summary
    if results:
        avg_greedy_exp = sum(r['greedy_expanded'] for r in results) / len(results)
        avg_astar_exp  = sum(r['astar_expanded']  for r in results) / len(results)
        avg_greedy_len = sum(r['greedy_length']   for r in results) / len(results)
        avg_astar_len  = sum(r['astar_length']    for r in results) / len(results)

        print(f"\n--- {city_name} Summary ---")
        print(f"  Avg nodes expanded  →  Greedy: {avg_greedy_exp:,.0f}  |  A*: {avg_astar_exp:,.0f}")
        print(f"  Avg path length     →  Greedy: {avg_greedy_len:,.0f}m  |  A*: {avg_astar_len:,.0f}m")

    return results

# Run experiments
random.seed(42)
baku_results    = run_experiment(baku,    "Baku, Azerbaijan")
tbilisi_results = run_experiment(tbilisi, "Tbilisi, Georgia")