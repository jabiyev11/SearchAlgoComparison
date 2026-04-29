import heapq
import math

def haversine(node1_data, node2_data):
    lat1, lon1 = math.radians(node1_data['y']), math.radians(node1_data['x'])
    lat2, lon2 = math.radians(node2_data['y']), math.radians(node2_data['x'])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 6371000 * 2 * math.asin(math.sqrt(a))


def _greedy_core(graph, start, goal):
    goal_data = graph.nodes[goal]
    frontier = [(0, start, [start])]
    visited = set()

    while frontier:
        _, current, path = heapq.heappop(frontier)
        if current in visited:
            continue
        visited.add(current)

        node_data = graph.nodes[current]
        yield ('expand', current, node_data)

        if current == goal:
            total_length = sum(
                graph[path[i]][path[i+1]][0].get('length', 0)
                for i in range(len(path) - 1)
            )
            yield ('done', path, len(visited), total_length)
            return

        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                h = haversine(graph.nodes[neighbor], goal_data)
                heapq.heappush(frontier, (h, neighbor, path + [neighbor]))

    yield ('no_path', len(visited))


def _astar_core(graph, start, goal):
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
        yield ('expand', current, node_data)

        if current == goal:
            yield ('done', path, len(visited), g)
            return

        for neighbor in graph.neighbors(current):
            edge_length = graph[current][neighbor][0].get('length', 0)
            new_g = g + edge_length
            h = haversine(graph.nodes[neighbor], goal_data)
            heapq.heappush(frontier, (new_g + h, neighbor, new_g, path + [neighbor]))

    yield ('no_path', len(visited))


def greedy_best_first_search(graph, start, goal):
    for event in _greedy_core(graph, start, goal):
        if event[0] == 'done':
            _, path, nodes_expanded, path_length = event
            return {'path': path, 'nodes_expanded': nodes_expanded,
                    'path_length': path_length, 'found': True}
        elif event[0] == 'no_path':
            return {'found': False, 'nodes_expanded': event[1]}
    return {'found': False, 'nodes_expanded': 0}


def astar_search(graph, start, goal):
    for event in _astar_core(graph, start, goal):
        if event[0] == 'done':
            _, path, nodes_expanded, path_length = event
            return {'path': path, 'nodes_expanded': nodes_expanded,
                    'path_length': path_length, 'found': True}
        elif event[0] == 'no_path':
            return {'found': False, 'nodes_expanded': event[1]}
    return {'found': False, 'nodes_expanded': 0}

def greedy_stream(graph, start, goal):
    for event in _greedy_core(graph, start, goal):
        if event[0] == 'expand':
            _, node_id, node_data = event
            yield {'type': 'expand', 'lat': node_data['y'], 'lon': node_data['x']}
        elif event[0] == 'done':
            _, path, nodes_expanded, path_length = event
            coords = [{'lat': graph.nodes[n]['y'], 'lon': graph.nodes[n]['x']} for n in path]
            yield {'type': 'done', 'path': coords,
                   'nodes_expanded': nodes_expanded, 'path_length': round(path_length)}
        elif event[0] == 'no_path':
            yield {'type': 'no_path'}


def astar_stream(graph, start, goal):
    for event in _astar_core(graph, start, goal):
        if event[0] == 'expand':
            _, node_id, node_data = event
            yield {'type': 'expand', 'lat': node_data['y'], 'lon': node_data['x']}
        elif event[0] == 'done':
            _, path, nodes_expanded, path_length = event
            coords = [{'lat': graph.nodes[n]['y'], 'lon': graph.nodes[n]['x']} for n in path]
            yield {'type': 'done', 'path': coords,
                   'nodes_expanded': nodes_expanded, 'path_length': round(path_length)}
        elif event[0] == 'no_path':
            yield {'type': 'no_path'}