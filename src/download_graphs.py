import osmnx as ox

print("Downloading Baku road network...")
baku_graph = ox.graph_from_place("Baku, Azerbaijan", network_type="drive")
print(f"Baku: {len(baku_graph.nodes)} nodes, {len(baku_graph.edges)} edges")

print("\nDownloading Tbilisi road network...")
tbilisi_graph = ox.graph_from_place("Tbilisi, Georgia", network_type="drive")
print(f"Tbilisi: {len(tbilisi_graph.nodes)} nodes, {len(tbilisi_graph.edges)} edges")

print("\nSaving graphs to disk...")
ox.save_graphml(baku_graph, "graphs/baku.graphml")
ox.save_graphml(tbilisi_graph, "graphs/tbilisi.graphml")
print("Saved!")