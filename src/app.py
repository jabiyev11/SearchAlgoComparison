from flask import Flask, render_template, jsonify, Response
from search_algorithms import greedy_best_first_search, astar_search, greedy_stream, astar_stream
import osmnx as ox
import json
import random
import time

app = Flask(__name__)

# Load graphs once at startup
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

def get_nearest_node(graph, lat, lon):
    return ox.distance.nearest_nodes(graph, lon, lat)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream/<algo>/<city>/<float:start_lat>/<float:start_lon>/<float:goal_lat>/<float:goal_lon>')
def stream(algo, city, start_lat, start_lon, goal_lat, goal_lon):
    graph = GRAPHS[city]
    start = get_nearest_node(graph, start_lat, start_lon)
    goal  = get_nearest_node(graph, goal_lat,  goal_lon)

    algo_fn = greedy_stream if algo == 'greedy' else astar_stream

    def generate():
        for step in algo_fn(graph, start, goal):
            yield f"data: {json.dumps(step)}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/cities')
def cities():
    return jsonify(CITY_CENTERS)

@app.route('/experiment/<city>/<int:num_pairs>')
def experiment(city, num_pairs):
    graph = GRAPHS[city]
    nodes = list(graph.nodes)
    results = []

    for i in range(num_pairs):
        start, goal = random.sample(nodes, 2)

        t0 = time.time()
        greedy = greedy_best_first_search(graph, start, goal)
        greedy_time = time.time() - t0

        t0 = time.time()
        astar = astar_search(graph, start, goal)
        astar_time = time.time() - t0

        if greedy['found'] and astar['found']:
            start_coords = {'lat': graph.nodes[start]['y'], 'lon': graph.nodes[start]['x']}
            goal_coords  = {'lat': graph.nodes[goal]['y'],  'lon': graph.nodes[goal]['x']}
            results.append({
                'pair': i + 1,
                'start': start_coords,
                'goal': goal_coords,
                'greedy_nodes': greedy['nodes_expanded'],
                'greedy_length': round(greedy['path_length'], 1),
                'greedy_time': round(greedy_time * 1000, 1),
                'astar_nodes': astar['nodes_expanded'],
                'astar_length': round(astar['path_length'], 1),
                'astar_time': round(astar_time * 1000, 1),
            })

    if results:
        avg = {
            'greedy_nodes': round(sum(r['greedy_nodes'] for r in results) / len(results)),
            'greedy_length': round(sum(r['greedy_length'] for r in results) / len(results), 1),
            'greedy_time': round(sum(r['greedy_time'] for r in results) / len(results), 1),
            'astar_nodes': round(sum(r['astar_nodes'] for r in results) / len(results)),
            'astar_length': round(sum(r['astar_length'] for r in results) / len(results), 1),
            'astar_time': round(sum(r['astar_time'] for r in results) / len(results), 1),
        }
    else:
        avg = {}

    return jsonify({'results': results, 'averages': avg, 'city': city})

if __name__ == '__main__':
    app.run(debug=True)