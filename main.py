import heapq
import math
import sys


def calculate_heuristic(current_square_id, goal_square_id):
    row_start = current_square_id // 10
    col_start = current_square_id % 10

    row_goal = goal_square_id // 10
    col_goal = goal_square_id % 10
    delta_row = abs(row_start - row_goal)
    delta_col = abs(col_start - col_goal)
    y_dist = max(0, delta_row - 1) * 10
    x_dist = max(0, delta_col - 1) * 10
    return math.sqrt(x_dist ** 2 + y_dist ** 2) * 100.0


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.start_node = None
        self.end_node = None

    def add_node(self, node_id, square_id):
        self.nodes[node_id] = square_id
        if node_id not in self.edges:
            self.edges[node_id] = []

    def add_edge(self, u, v, dist):
        self.edges[u].append((v, dist))

    def get_square(self, node_id):
        return self.nodes.get(node_id)


def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]


def run_search(graph, start_node, end_node, algorithm="dijkstra"):
    pq = []
    heapq.heappush(pq, (0, start_node))
    g_score = {start_node: 0}
    came_from = {}
    visited = set()
    nodes_expanded = 0
    end_square = graph.get_square(end_node)
    while pq:
        current_priority, current_node = heapq.heappop(pq)
        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == end_node:
            return {
                "found": True,
                "distance": g_score[current_node],
                "path": reconstruct_path(came_from, current_node),
                "nodes_expanded": nodes_expanded
            }

        nodes_expanded += 1
        if current_node in graph.edges:
            for neighbor, weight in graph.edges[current_node]:
                tentative_g = g_score[current_node] + weight
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current_node
                    g_score[neighbor] = tentative_g
                    priority = tentative_g
                    if algorithm == "astar":
                        neighbor_square = graph.get_square(neighbor)
                        h_cost = calculate_heuristic(neighbor_square, end_square)
                        priority = tentative_g + h_cost

                    heapq.heappush(pq, (priority, neighbor))

    return {"found": False, "nodes_expanded": nodes_expanded}


def load_graph_from_file(filename):
    g = Graph()
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue

            if "//" in line:
                line = line.split("//")[0].strip()
            if "#" in line:
                line = line.split("#")[0].strip()

            parts = line.split(',')
            if len(parts) >= 2:
                if parts[0].strip().upper() == 'S':
                    g.start_node = int(parts[1])
                    continue
                if parts[0].strip().upper() == 'D':
                    g.end_node = int(parts[1])
                    continue

            if len(parts) == 2:
                node_id = int(parts[0])
                square_id = int(parts[1])
                g.add_node(node_id, square_id)
            elif len(parts) == 3:
                u = int(parts[0])
                v = int(parts[1])
                dist = float(parts[2])
                g.add_edge(u, v, dist)

        return g
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None




if __name__ == "__main__":
    input_file = "p1_graph.txt"
    cli_start = None
    cli_end = None

    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    if len(sys.argv) > 3:
        try:
            cli_start = int(sys.argv[2])
            cli_end = int(sys.argv[3])
        except ValueError:
            print("Error: Start and End nodes must be integers.")
            sys.exit(1)

    graph = load_graph_from_file(input_file)

    if graph:
        start_node = 0
        end_node = 50

        if graph.start_node is not None:
            start_node = graph.start_node
        if graph.end_node is not None:
            end_node = graph.end_node

        if cli_start is not None:
            start_node = cli_start
        if cli_end is not None:
            end_node = cli_end
        if start_node not in graph.nodes or end_node not in graph.nodes:
            print("Start or End node not found in graph keys.")
        else:
            print(
                f"\nCalculating path from Node {start_node} (Sq: {graph.get_square(start_node)}) to Node {end_node} (Sq: {graph.get_square(end_node)})...\n")

            dijkstra_result = run_search(graph, start_node, end_node, "dijkstra")
            astar_result = run_search(graph, start_node, end_node, "astar")

            print(f"{'Algorithm':<15} | {'Cost':<10} | {'Nodes Expanded':<15} | {'Path Found'}")

            if dijkstra_result['found']:
                print(
                    f"{'Dijkstra':<15} | {dijkstra_result['distance']:<10.2f} | {dijkstra_result['nodes_expanded']:<15} | Yes")
            else:
                print(f"{'Dijkstra':<15} | {'N/A':<10} | {dijkstra_result['nodes_expanded']:<15} | No")

            if astar_result['found']:
                print(
                    f"{'A* (Star)':<15} | {astar_result['distance']:<10.2f} | {astar_result['nodes_expanded']:<15} | Yes")
            else:
                print(f"{'A* (Star)':<15} | {'N/A':<10} | {astar_result['nodes_expanded']:<15} | No")

            if dijkstra_result['found']:
                print(f"Path (Dijkstra): {dijkstra_result['path']}")