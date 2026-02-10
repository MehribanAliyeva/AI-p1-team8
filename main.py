import heapq
import math
import sys
import time
import tracemalloc


# Estimates the straight-line distance between two squares on the grid.
# Each square ID encodes its row (tens digit) and column (ones digit),
# so we can derive grid coordinates and compute Euclidean distance.
def calculate_heuristic(current_square_id, goal_square_id):
    # Extract row and column from the square ID
    row_start = current_square_id // 10
    col_start = current_square_id % 10

    row_goal = goal_square_id // 10
    col_goal = goal_square_id % 10
    delta_row = abs(row_start - row_goal)
    delta_col = abs(col_start - col_goal)

    # Subtract 1 from each delta to account for the size of the squares themselves,
    # then scale by 10 to get the actual grid distance in each direction.
    y_dist = max(0, delta_row - 1) * 10
    x_dist = max(0, delta_col - 1) * 10

    # Multiply by 100 to keep the heuristic in the same scale as edge weights
    return math.sqrt(x_dist ** 2 + y_dist ** 2) * 100.0


# Simple directed graph that maps node IDs to grid square IDs and stores weighted edges as an adjacency list.
class Graph:
    def __init__(self):
        self.nodes = {}        # node_id -> square_id
        self.edges = {}        # node_id -> list of (neighbor_id, weight)
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


# Walks backwards through the came_from map to rebuild the full path
# from start to the given node, then reverses it so it reads start-to-end.
def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]


# Unified search function that handles both Dijkstra and A*.
# The only difference is how the priority is computed: Dijkstra uses
# just the path cost g(n), while A* adds the heuristic h(n) on top.
def run_search(graph, start_node, end_node, algorithm="dijkstra"):
    pq = []
    heapq.heappush(pq, (0, start_node))
    g_score = {start_node: 0}  # best known cost to reach each node
    came_from = {}             # tracks the parent of each visited node
    visited = set()
    nodes_expanded = 0
    end_square = graph.get_square(end_node)

    while pq:
        current_priority, current_node = heapq.heappop(pq)

        # Skip nodes we already fully processed
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

                # Only update if we found a cheaper way to reach this neighbor
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current_node
                    g_score[neighbor] = tentative_g

                    # For A*, add the heuristic estimate to the priority
                    priority = tentative_g
                    if algorithm == "astar":
                        neighbor_square = graph.get_square(neighbor)
                        h_cost = calculate_heuristic(neighbor_square, end_square)
                        priority = tentative_g + h_cost

                    heapq.heappush(pq, (priority, neighbor))

    # If we exhaust the queue without reaching the goal, no path exists
    return {"found": False, "nodes_expanded": nodes_expanded}


# Reads a graph definition from a text file. The format supports:
#   - Two-column lines (node_id, square_id) for vertices
#   - Three-column lines (from, to, distance) for directed edges
#   - S,<id> and D,<id> lines to set the default start and destination
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

            # Two values means it is a node definition, three means an edge
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

    # Usage: python main.py [graph_file] [start_node end_node]
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

            # Run Dijkstra and measure wall-clock time and peak memory
            tracemalloc.start()
            t0 = time.perf_counter()
            dijkstra_result = run_search(graph, start_node, end_node, "dijkstra")
            t1 = time.perf_counter()
            dijkstra_mem = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            dijkstra_result['time_ms'] = (t1 - t0) * 1000
            dijkstra_result['peak_memory_kb'] = dijkstra_mem / 1024

            # Same thing for A*
            tracemalloc.start()
            t0 = time.perf_counter()
            astar_result = run_search(graph, start_node, end_node, "astar")
            t1 = time.perf_counter()
            astar_mem = tracemalloc.get_traced_memory()[1]  # peak
            tracemalloc.stop()
            astar_result['time_ms'] = (t1 - t0) * 1000
            astar_result['peak_memory_kb'] = astar_mem / 1024

            header = f"{'Algorithm':<15} | {'Cost':<10} | {'Nodes Expanded':<15} | {'Time (ms)':<12} | {'Peak Mem (KB)':<14} | {'Path Found'}"
            print(header)
            print('-' * len(header))

            for label, result in [("Dijkstra", dijkstra_result), ("A* (Star)", astar_result)]:
                if result['found']:
                    print(f"{label:<15} | {result['distance']:<10.2f} | {result['nodes_expanded']:<15} | "
                          f"{result['time_ms']:<12.4f} | {result['peak_memory_kb']:<14.2f} | Yes")
                else:
                    print(f"{label:<15} | {'N/A':<10} | {result['nodes_expanded']:<15} | "
                          f"{result['time_ms']:<12.4f} | {result['peak_memory_kb']:<14.2f} | No")

            if dijkstra_result['found']:
                print(f"\nPath (Dijkstra): {dijkstra_result['path']}")
            if astar_result['found']:
                print(f"Path (A*):       {astar_result['path']}")