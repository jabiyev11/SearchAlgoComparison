import osmnx as ox
import networkx as nx

# Load graphs
print("Loading graphs...")
baku = ox.load_graphml("graphs/baku.graphml")
tbilisi = ox.load_graphml("graphs/tbilisi.graphml")
print("Loaded!\n")

def check_connectivity(graph, name):
    undirected = graph.to_undirected()
    components = list(nx.connected_components(undirected))
    sizes = sorted([len(c) for c in components], reverse=True)

    print(f"{'=' * 50}")
    print(f"  {name} — Connectivity Check")
    print(f"{'=' * 50}")
    print(f"  Total nodes:             {len(graph.nodes):,}")
    print(f"  Total components:        {len(components)}")
    print(f"  Largest component:       {sizes[0]:,} nodes ({sizes[0]/len(graph.nodes)*100:.1f}%)")
    if len(sizes) > 1:
        print(f"  2nd largest component:   {sizes[1]:,} nodes")
        print(f"  Smallest component:      {sizes[-1]:,} nodes")
        isolated = sum(1 for s in sizes if s == 1)
        print(f"  Isolated nodes:          {isolated}")
        print(f"  → Graph has disconnected parts — some node pairs may be unreachable!")
    else:
        print(f"  → Graph is fully connected — all nodes are reachable.")
    print()

check_connectivity(baku, "Baku, Azerbaijan")
check_connectivity(tbilisi, "Tbilisi, Georgia")