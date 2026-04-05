import heapq  # like Java's PriorityQueue
import math

def haversine(node1_data, node2_data):
    """
    Calculates real-world distance between two GPS points.
    This is our heuristic function h(n).
    Like a static utility method in Java.
    """
    lat1, lon1 = math.radians(node1_data['y']), math.radians(node1_data['x'])
    lat2, lon2 = math.radians(node2_data['y']), math.radians(node2_data['x'])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 6371000 * 2 * math.asin(math.sqrt(a))  # result in meters


def greedy_best_first_search(graph, start, goal):
    """
    Greedy Best-First Search.
    Only uses h(n) — how close am I to the goal?
    Like a traveler who always walks toward the destination, ignoring path cost.
    """
    goal_data = graph.nodes[goal]

    # Priority queue: (heuristic, node, path)
    # In Java: PriorityQueue<int[]> ordered by heuristic
    frontier = [(0, start, [start])]
    visited = set()  # like Java's HashSet<Integer>
    nodes_expanded = 0

    while frontier:
        _, current, path = heapq.heappop(frontier)

        if current in visited:
            continue
        visited.add(current)
        nodes_expanded += 1

        if current == goal:
            total_length = sum(
                graph[path[i]][path[i+1]][0].get('length', 0)
                for i in range(len(path) - 1)
            )
            return {
                'path': path,
                'nodes_expanded': nodes_expanded,
                'path_length': total_length,
                'found': True
            }

        # Expand neighbors — like iterating adjacency list in Java
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                h = haversine(graph.nodes[neighbor], goal_data)
                heapq.heappush(frontier, (h, neighbor, path + [neighbor]))

    return {'found': False, 'nodes_expanded': nodes_expanded}


def astar_search(graph, start, goal):
    """
    A* Search.
    Uses f(n) = g(n) + h(n) — actual cost so far + estimated cost to goal.
    Guaranteed to find the shortest path.
    """
    goal_data = graph.nodes[goal]

    # Priority queue: (f_score, node, g_score, path)
    start_h = haversine(graph.nodes[start], goal_data)
    frontier = [(start_h, start, 0, [start])]
    visited = {}  # node -> best g_score seen, like Java's HashMap<Integer, Double>
    nodes_expanded = 0

    while frontier:
        f, current, g, path = heapq.heappop(frontier)

        if current in visited and visited[current] <= g:
            continue
        visited[current] = g
        nodes_expanded += 1

        if current == goal:
            return {
                'path': path,
                'nodes_expanded': nodes_expanded,
                'path_length': g,
                'found': True
            }

        for neighbor in graph.neighbors(current):
            edge_data = graph[current][neighbor][0]
            edge_length = edge_data.get('length', 0)
            new_g = g + edge_length
            h = haversine(graph.nodes[neighbor], goal_data)
            f_score = new_g + h
            heapq.heappush(frontier, (f_score, neighbor, new_g, path + [neighbor]))

    return {'found': False, 'nodes_expanded': nodes_expanded}