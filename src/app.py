from flask import Flask, render_template, request, jsonify, Response
import osmnx as ox
import json
import math

app = Flask(__name__)

# Load graphs once at startup — like a @PostConstruct in Spring Boot
print("Loading graphs...")
GRAPHS = {
    "baku": ox.load_graphml("graphs/baku.graphml"),
    "tbilisi": ox.load_graphml("graphs/tbilisi.graphml")
}
print("Graphs loaded! ✅")

CITY_CENTERS = {
    "baku":    [40.4093, 49.8671],
    "tbilisi": [41.6938, 44.8015]
}

def haversine(node1_data, node2_data):
    lat1, lon1 = math.radians(node1_data['y']), math.radians(node1_data['x'])
    lat2, lon2 = math.radians(node2_data['y']), math.radians(node2_data['x'])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 6371000 * 2 * math.asin(math.sqrt(a))

def get_nearest_node(graph, lat, lon):
    return ox.distance.nearest_nodes(graph, lon, lat)

def greedy_steps(graph, start, goal):
    """Yields each step so we can stream it to the frontend"""
    import heapq
    goal_data = graph.nodes[goal]
    frontier = [(0, start, [start])]
    visited = set()

    while frontier:
        _, current, path = heapq.heappop(frontier)
        if current in visited:
            continue
        visited.add(current)

        # Yield this expansion step
        node_data = graph.nodes[current]
        yield {'type': 'expand', 'lat': node_data['y'], 'lon': node_data['x']}

        if current == goal:
            coords = [{'lat': graph.nodes[n]['y'], 'lon': graph.nodes[n]['x']} for n in path]
            total_length = sum(
                graph[path[i]][path[i+1]][0].get('length', 0)
                for i in range(len(path) - 1)
            )
            yield {'type': 'done', 'path': coords,
                   'nodes_expanded': len(visited), 'path_length': round(total_length)}
            return

        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                h = haversine(graph.nodes[neighbor], goal_data)
                heapq.heappush(frontier, (h, neighbor, path + [neighbor]))

    yield {'type': 'no_path'}

def astar_steps(graph, start, goal):
    """Yields each step so we can stream it to the frontend"""
    import heapq
    goal_data = graph.nodes[goal]
    start_h = haversine(graph.nodes[start], goal_data)
    frontier = [(start_h, start, 0, [start])]
    visited = {}

    while frontier:
        f, current, g, path = heapq.heappop(frontier)
        if current in visited and visited[current] <= g:
            continue
        visited[current] = g

        node_data = graph.nodes[current]
        yield {'type': 'expand', 'lat': node_data['y'], 'lon': node_data['x']}

        if current == goal:
            coords = [{'lat': graph.nodes[n]['y'], 'lon': graph.nodes[n]['x']} for n in path]
            yield {'type': 'done', 'path': coords,
                   'nodes_expanded': len(visited), 'path_length': round(g)}
            return

        for neighbor in graph.neighbors(current):
            edge_length = graph[current][neighbor][0].get('length', 0)
            new_g = g + edge_length
            h = haversine(graph.nodes[neighbor], goal_data)
            heapq.heappush(frontier, (new_g + h, neighbor, new_g, path + [neighbor]))

    yield {'type': 'no_path'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream/<algo>/<city>/<float:start_lat>/<float:start_lon>/<float:goal_lat>/<float:goal_lon>')
def stream(algo, city, start_lat, start_lon, goal_lat, goal_lon):
    graph = GRAPHS[city]
    start = get_nearest_node(graph, start_lat, start_lon)
    goal  = get_nearest_node(graph, goal_lat,  goal_lon)

    algo_fn = greedy_steps if algo == 'greedy' else astar_steps

    def generate():
        for step in algo_fn(graph, start, goal):
            yield f"data: {json.dumps(step)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/cities')
def cities():
    return jsonify(CITY_CENTERS)

if __name__ == '__main__':
    app.run(debug=True)