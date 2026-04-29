import osmnx as ox
import folium
import random
from search_algorithms import greedy_best_first_search, astar_search

# Load graphs
print("Loading graphs...")
baku = ox.load_graphml("graphs/baku.graphml")
tbilisi = ox.load_graphml("graphs/tbilisi.graphml")
print("Loaded! ✅")

def get_node_coords(graph, node):
    """Returns (lat, lon) for a node — folium uses lat/lon order"""
    data = graph.nodes[node]
    return (data['y'], data['x'])

def visualize_comparison(graph, city_name, start, goal, filename):
    """
    Creates a dual-view Folium map showing both algorithm routes side by side.
    """
    print(f"\nRunning algorithms for {city_name}...")
    greedy_result = greedy_best_first_search(graph, start, goal)
    astar_result  = astar_search(graph, start, goal)

    if not greedy_result['found'] or not astar_result['found']:
        print("Could not find path!")
        return

    # Get center of map
    start_coords = get_node_coords(graph, start)
    goal_coords  = get_node_coords(graph, goal)
    center_lat   = (start_coords[0] + goal_coords[0]) / 2
    center_lon   = (start_coords[1] + goal_coords[1]) / 2

    # Build Folium map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="CartoDB positron")

    # --- Draw Greedy path in RED ---
    greedy_coords = [get_node_coords(graph, n) for n in greedy_result['path']]
    folium.PolyLine(
        greedy_coords,
        color='red',
        weight=4,
        opacity=0.8,
        tooltip=f"Greedy | {greedy_result['path_length']:,.0f}m | {greedy_result['nodes_expanded']} nodes expanded"
    ).add_to(m)

    # --- Draw A* path in BLUE ---
    astar_coords = [get_node_coords(graph, n) for n in astar_result['path']]
    folium.PolyLine(
        astar_coords,
        color='blue',
        weight=4,
        opacity=0.8,
        tooltip=f"A* | {astar_result['path_length']:,.0f}m | {astar_result['nodes_expanded']} nodes expanded"
    ).add_to(m)

    # --- Start marker (green) ---
    folium.Marker(
        start_coords,
        popup="START",
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)

    # --- Goal marker (red) ---
    folium.Marker(
        goal_coords,
        popup="GOAL",
        icon=folium.Icon(color='red', icon='flag')
    ).add_to(m)

    # --- Legend ---
    legend_html = f"""
    <div style="position: fixed; bottom: 40px; left: 40px; z-index: 1000;
                background: white; padding: 15px; border-radius: 10px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.3); font-family: Arial;">
        <h4 style="margin:0 0 10px 0">{city_name}</h4>
        <p style="margin:4px 0"><span style="color:red">●</span>
            <b>Greedy</b>: {greedy_result['path_length']:,.0f}m &nbsp;|&nbsp;
            {greedy_result['nodes_expanded']:,} nodes expanded</p>
        <p style="margin:4px 0"><span style="color:blue">●</span>
            <b>A*</b>: {astar_result['path_length']:,.0f}m &nbsp;|&nbsp;
            {astar_result['nodes_expanded']:,} nodes expanded</p>
        <p style="margin:4px 0; color:gray; font-size:12px">
            Greedy is {(greedy_result['path_length']/astar_result['path_length']-1)*100:.1f}% longer than A*</p>
        <p style="margin:4px 0; color:gray; font-size:12px">
            Hover over routes to see details</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(filename)
    print(f"Saved → {filename}")
    print(f"  Greedy: {greedy_result['path_length']:,.0f}m, {greedy_result['nodes_expanded']} nodes")
    print(f"  A*:     {astar_result['path_length']:,.0f}m, {astar_result['nodes_expanded']} nodes")


# Use the same seed as experiments for reproducibility
random.seed(42)
baku_nodes    = list(baku.nodes)
tbilisi_nodes = list(tbilisi.nodes)

# Pick the same pairs as experiments.py (pair 3 — most dramatic difference)
random.sample(baku_nodes, 2)  # skip pair 1
random.sample(baku_nodes, 2)  # skip pair 2
baku_pair = random.sample(baku_nodes, 2)  # pair 3

random.seed(42)
random.sample(tbilisi_nodes, 2)  # skip pair 1
random.sample(tbilisi_nodes, 2)  # skip pair 2
tbilisi_pair = random.sample(tbilisi_nodes, 2)  # pair 3

visualize_comparison(baku,    "Baku, Azerbaijan", baku_pair[0], baku_pair[1], "static/baku_map.html")
visualize_comparison(tbilisi, "Tbilisi, Georgia", tbilisi_pair[0], tbilisi_pair[1], "static/tbilisi_map.html")

print("\nDone! Open baku_map.html and tbilisi_map.html in your browser 🗺️")