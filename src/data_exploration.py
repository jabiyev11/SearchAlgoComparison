import osmnx as ox
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("figures", exist_ok=True)

print("Loading graphs...")
baku = ox.load_graphml("graphs/baku.graphml")
tbilisi = ox.load_graphml("graphs/tbilisi.graphml")
print("Loaded!\n")

def graph_stats(graph, name):
    num_nodes = len(graph.nodes)
    num_edges = len(graph.edges)
    degrees = [d for _, d in graph.degree()]
    avg_degree = sum(degrees) / len(degrees)

    # Edge lengths
    lengths = []
    missing_length = 0
    for u, v, data in graph.edges(data=True):
        if 'length' in data:
            lengths.append(float(data['length']))
        else:
            missing_length += 1

    print(f"{'=' * 50}")
    print(f"  {name}")
    print(f"{'=' * 50}")
    print(f"  Nodes:              {num_nodes:,}")
    print(f"  Edges:              {num_edges:,}")
    print(f"  Avg degree:         {avg_degree:.2f}")
    print(f"  Edges with length:  {len(lengths):,}")
    print(f"  Missing length:     {missing_length:,}")
    if lengths:
        print(f"  Edge length min:    {min(lengths):.1f} m")
        print(f"  Edge length max:    {max(lengths):.1f} m")
        print(f"  Edge length mean:   {np.mean(lengths):.1f} m")
        print(f"  Edge length median: {np.median(lengths):.1f} m")
        print(f"  Edge length std:    {np.std(lengths):.1f} m")
    print()
    return lengths, degrees

baku_lengths, baku_degrees = graph_stats(baku, "Baku, Azerbaijan")
tbilisi_lengths, tbilisi_degrees = graph_stats(tbilisi, "Tbilisi, Georgia")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(baku_lengths, bins=80, color='#3498db', edgecolor='white', alpha=0.85)
axes[0].set_title("Baku — Edge Length Distribution", fontsize=14, fontweight='bold')
axes[0].set_xlabel("Edge Length (meters)")
axes[0].set_ylabel("Frequency")
axes[0].axvline(np.median(baku_lengths), color='red', linestyle='--', label=f'Median: {np.median(baku_lengths):.0f}m')
axes[0].legend()
axes[0].set_xlim(0, 1000)

axes[1].hist(tbilisi_lengths, bins=80, color='#e67e22', edgecolor='white', alpha=0.85)
axes[1].set_title("Tbilisi — Edge Length Distribution", fontsize=14, fontweight='bold')
axes[1].set_xlabel("Edge Length (meters)")
axes[1].set_ylabel("Frequency")
axes[1].axvline(np.median(tbilisi_lengths), color='red', linestyle='--', label=f'Median: {np.median(tbilisi_lengths):.0f}m')
axes[1].legend()
axes[1].set_xlim(0, 1000)

plt.tight_layout()
plt.savefig("figures/edge_length_distribution.png", dpi=200, bbox_inches='tight')
plt.close()
print("Saved: figures/edge_length_distribution.png")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(baku_degrees, bins=range(1, max(baku_degrees) + 2), color='#3498db', edgecolor='white', alpha=0.85, align='left')
axes[0].set_title("Baku — Node Degree Distribution", fontsize=14, fontweight='bold')
axes[0].set_xlabel("Degree (number of connections)")
axes[0].set_ylabel("Frequency")

axes[1].hist(tbilisi_degrees, bins=range(1, max(tbilisi_degrees) + 2), color='#e67e22', edgecolor='white', alpha=0.85, align='left')
axes[1].set_title("Tbilisi — Node Degree Distribution", fontsize=14, fontweight='bold')
axes[1].set_xlabel("Degree (number of connections)")
axes[1].set_ylabel("Frequency")

plt.tight_layout()
plt.savefig("figures/degree_distribution.png", dpi=200, bbox_inches='tight')
plt.close()
print("Saved: figures/degree_distribution.png")

fig, axes = plt.subplots(1, 2, figsize=(18, 8))

ox.plot_graph(baku, ax=axes[0], node_size=0, edge_linewidth=0.3, edge_color='#3498db', bgcolor='white', show=False, close=False)
axes[0].set_title("Baku Road Network", fontsize=16, fontweight='bold')

ox.plot_graph(tbilisi, ax=axes[1], node_size=0, edge_linewidth=0.3, edge_color='#e67e22', bgcolor='white', show=False, close=False)
axes[1].set_title("Tbilisi Road Network", fontsize=16, fontweight='bold')

plt.tight_layout()
plt.savefig("figures/road_networks.png", dpi=200, bbox_inches='tight')
plt.close()
print("Saved: figures/road_networks.png")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

cities = ['Baku', 'Tbilisi']
colors = ['#3498db', '#e67e22']

# Nodes
axes[0].bar(cities, [len(baku.nodes), len(tbilisi.nodes)], color=colors, edgecolor='white')
axes[0].set_title("Number of Nodes", fontsize=13, fontweight='bold')
for i, v in enumerate([len(baku.nodes), len(tbilisi.nodes)]):
    axes[0].text(i, v + 500, f'{v:,}', ha='center', fontweight='bold')

# Edges
axes[1].bar(cities, [len(baku.edges), len(tbilisi.edges)], color=colors, edgecolor='white')
axes[1].set_title("Number of Edges", fontsize=13, fontweight='bold')
for i, v in enumerate([len(baku.edges), len(tbilisi.edges)]):
    axes[1].text(i, v + 500, f'{v:,}', ha='center', fontweight='bold')

# Avg edge length
baku_avg = np.mean(baku_lengths)
tbilisi_avg = np.mean(tbilisi_lengths)
axes[2].bar(cities, [baku_avg, tbilisi_avg], color=colors, edgecolor='white')
axes[2].set_title("Avg Edge Length (m)", fontsize=13, fontweight='bold')
for i, v in enumerate([baku_avg, tbilisi_avg]):
    axes[2].text(i, v + 2, f'{v:.1f}', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig("figures/comparison_summary.png", dpi=200, bbox_inches='tight')
plt.close()
print("Saved: figures/comparison_summary.png")

print("\nDone! All figures saved to figures/ folder.")