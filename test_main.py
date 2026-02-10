import math
import os
import unittest

from main import Graph, calculate_heuristic, load_graph_from_file, reconstruct_path, run_search


# Heuristic tests

class TestCalculateHeuristic(unittest.TestCase):
    def test_same_square_returns_zero(self):
        # Two nodes sitting on the same square should have zero estimated distance
        self.assertEqual(calculate_heuristic(55, 55), 0.0)

    def test_adjacent_squares_same_row(self):
        # Squares next to each other horizontally (e.g. 11 and 12) are within
        # one step, so the delta minus 1 is zero in both directions
        self.assertEqual(calculate_heuristic(11, 12), 0.0)

    def test_adjacent_squares_same_column(self):
        # Same idea but vertically adjacent
        self.assertEqual(calculate_heuristic(11, 21), 0.0)

    def test_diagonal_adjacent(self):
        # Diagonally adjacent squares (delta 1 in each direction) also
        # clamp to zero after subtracting 1
        self.assertEqual(calculate_heuristic(11, 22), 0.0)

    def test_known_distance(self):
        # Square 00 to 99: row diff 9, col diff 9 -> y_dist=80, x_dist=80
        # sqrt(80^2 + 80^2) * 100 = sqrt(12800) * 100
        expected = math.sqrt(80**2 + 80**2) * 100.0
        self.assertAlmostEqual(calculate_heuristic(0, 99), expected, places=4)

    def test_horizontal_far_apart(self):
        # Square 10 to 19: same row, col diff 9 -> x_dist=80, y_dist=0
        expected = 80 * 100.0
        self.assertAlmostEqual(calculate_heuristic(10, 19), expected, places=4)

    def test_vertical_far_apart(self):
        # Square 10 to 90: same col, row diff 8 -> y_dist=70, x_dist=0
        expected = 70 * 100.0
        self.assertAlmostEqual(calculate_heuristic(10, 90), expected, places=4)

    def test_heuristic_is_non_negative(self):
        # The heuristic should never return a negative value
        for a in range(0, 100, 17):
            for b in range(0, 100, 13):
                self.assertGreaterEqual(calculate_heuristic(a, b), 0.0)


# Graph construction

class TestGraph(unittest.TestCase):
    """Basic tests for building a graph and querying it."""

    def setUp(self):
        self.g = Graph()
        self.g.add_node(0, 11)
        self.g.add_node(1, 22)
        self.g.add_node(2, 33)
        self.g.add_edge(0, 1, 5.0)
        self.g.add_edge(1, 2, 3.0)

    def test_add_node(self):
        self.assertEqual(self.g.get_square(0), 11)
        self.assertEqual(self.g.get_square(1), 22)

    def test_get_square_missing(self):
        # Asking for a node that was never added should give None
        self.assertIsNone(self.g.get_square(999))

    def test_add_edge(self):
        neighbors = self.g.edges[0]
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0], (1, 5.0))

    def test_edges_initialized_on_add_node(self):
        # When we add a node, it should automatically get an empty neighbor list
        self.g.add_node(10, 44)
        self.assertIn(10, self.g.edges)
        self.assertEqual(self.g.edges[10], [])


# Path reconstruction

class TestReconstructPath(unittest.TestCase):

    def test_single_node_path(self):
        # If there is nothing in came_from, the path is just the node itself
        path = reconstruct_path({}, 5)
        self.assertEqual(path, [5])

    def test_linear_path(self):
        came_from = {3: 2, 2: 1, 1: 0}
        path = reconstruct_path(came_from, 3)
        self.assertEqual(path, [0, 1, 2, 3])

    def test_two_node_path(self):
        came_from = {1: 0}
        path = reconstruct_path(came_from, 1)
        self.assertEqual(path, [0, 1])


# Search algorithm tests

class TestRunSearch(unittest.TestCase):
    """Run Dijkstra and A* on small hand-crafted graphs."""

    def _make_line_graph(self):
        # Straight chain: 0 -> 1 -> 2, each node on its own square
        g = Graph()
        g.add_node(0, 0)
        g.add_node(1, 5)
        g.add_node(2, 9)
        g.add_edge(0, 1, 100)
        g.add_edge(1, 2, 200)
        return g

    def _make_diamond_graph(self):
        #     0
        #    / \
        #   1   2
        #    \ /
        #     3
        # Upper path costs 3+1=4, lower path costs 1+1=2, so 0->2->3 wins
        g = Graph()
        g.add_node(0, 0)
        g.add_node(1, 10)
        g.add_node(2, 1)
        g.add_node(3, 11)
        g.add_edge(0, 1, 3)
        g.add_edge(0, 2, 1)
        g.add_edge(1, 3, 1)
        g.add_edge(2, 3, 1)
        return g

    # Dijkstra on the line graph
    def test_dijkstra_finds_path_line(self):
        g = self._make_line_graph()
        result = run_search(g, 0, 2, "dijkstra")
        self.assertTrue(result["found"])
        self.assertEqual(result["distance"], 300)
        self.assertEqual(result["path"], [0, 1, 2])

    # A* on the line graph
    def test_astar_finds_path_line(self):
        g = self._make_line_graph()
        result = run_search(g, 0, 2, "astar")
        self.assertTrue(result["found"])
        self.assertEqual(result["distance"], 300)
        self.assertEqual(result["path"], [0, 1, 2])

    # Dijkstra should pick the shorter path through the diamond
    def test_dijkstra_shortest_path_diamond(self):
        g = self._make_diamond_graph()
        result = run_search(g, 0, 3, "dijkstra")
        self.assertTrue(result["found"])
        self.assertEqual(result["distance"], 2)
        self.assertEqual(result["path"], [0, 2, 3])

    def test_astar_shortest_path_diamond(self):
        g = self._make_diamond_graph()
        result = run_search(g, 0, 3, "astar")
        self.assertTrue(result["found"])
        self.assertEqual(result["distance"], 2)

    # Both algorithms should agree on the shortest distance
    def test_dijkstra_and_astar_same_cost(self):
        g = self._make_diamond_graph()
        d = run_search(g, 0, 3, "dijkstra")
        a = run_search(g, 0, 3, "astar")
        self.assertEqual(d["distance"], a["distance"])

    def test_no_path_exists(self):
        # Two disconnected nodes, so there is no way to get from 0 to 1
        g = Graph()
        g.add_node(0, 0)
        g.add_node(1, 99)
        result = run_search(g, 0, 1, "dijkstra")
        self.assertFalse(result["found"])

    def test_start_equals_end(self):
        # Searching from a node to itself should succeed immediately with cost 0
        g = Graph()
        g.add_node(0, 0)
        result = run_search(g, 0, 0, "dijkstra")
        self.assertTrue(result["found"])
        self.assertEqual(result["distance"], 0)
        self.assertEqual(result["path"], [0])

    def test_nodes_expanded_is_tracked(self):
        g = self._make_diamond_graph()
        result = run_search(g, 0, 3, "dijkstra")
        # We should have expanded at least one node before reaching the goal
        self.assertGreater(result["nodes_expanded"], 0)


class TestLoadGraphFromFile(unittest.TestCase):
    """Tests that load_graph_from_file parses various file formats correctly."""

    def _write_temp(self, content, filename="test_graph_tmp.txt"):
        path = os.path.join(os.path.dirname(__file__) or ".", filename)
        with open(path, "w") as f:
            f.write(content)
        return path

    def _cleanup(self, path):
        if os.path.exists(path):
            os.remove(path)

    def test_load_simple_graph(self):
        content = "0,10\n1,20\n0,1,500\nS,0\nD,1\n"
        path = self._write_temp(content)
        try:
            g = load_graph_from_file(path)
            self.assertIsNotNone(g)
            self.assertEqual(g.get_square(0), 10)
            self.assertEqual(g.get_square(1), 20)
            self.assertEqual(g.edges[0], [(1, 500.0)])
            self.assertEqual(g.start_node, 0)
            self.assertEqual(g.end_node, 1)
        finally:
            self._cleanup(path)

    def test_comments_and_blank_lines_are_skipped(self):
        content = "# This is a comment\n\n// Another comment\n0,55\n"
        path = self._write_temp(content)
        try:
            g = load_graph_from_file(path)
            self.assertEqual(len(g.nodes), 1)
            self.assertEqual(g.get_square(0), 55)
        finally:
            self._cleanup(path)

    def test_inline_comments_stripped(self):
        content = "0,10 // node zero\n1,20 # node one\n"
        path = self._write_temp(content)
        try:
            g = load_graph_from_file(path)
            self.assertEqual(g.get_square(0), 10)
            self.assertEqual(g.get_square(1), 20)
        finally:
            self._cleanup(path)

    def test_missing_file_returns_none(self):
        g = load_graph_from_file("this_file_does_not_exist.txt")
        self.assertIsNone(g)

    def test_load_real_graph_file(self):
        # Sanity check against the actual project graph if it exists
        real_path = os.path.join(os.path.dirname(__file__) or ".", "p1_graph.txt")
        if not os.path.exists(real_path):
            self.skipTest("p1_graph.txt not present")
        g = load_graph_from_file(real_path)
        self.assertIsNotNone(g)

        # The file defines 100 nodes (IDs 0 through 99)
        self.assertEqual(len(g.nodes), 100)

        # Start and destination markers should have been read
        self.assertEqual(g.start_node, 0)
        self.assertEqual(g.end_node, 99)

        # Make sure edges were loaded (the file has a lot of them)
        total_edges = sum(len(v) for v in g.edges.values())
        self.assertGreater(total_edges, 0)


# Integration full search on the project graph

class TestIntegrationWithProjectGraph(unittest.TestCase):
    """End-to-end tests on the actual p1_graph.txt file."""

    @classmethod
    def setUpClass(cls):
        real_path = os.path.join(os.path.dirname(__file__) or ".", "p1_graph.txt")
        cls.graph = load_graph_from_file(real_path)
        if cls.graph is None:
            raise unittest.SkipTest("p1_graph.txt not found, skipping integration tests")

    def test_dijkstra_finds_path_in_real_graph(self):
        result = run_search(self.graph, 0, 99, "dijkstra")
        self.assertTrue(result["found"])
        self.assertGreater(result["distance"], 0)

    def test_astar_finds_path_in_real_graph(self):
        result = run_search(self.graph, 0, 99, "astar")
        self.assertTrue(result["found"])
        self.assertGreater(result["distance"], 0)

    def test_both_algorithms_agree_on_cost(self):
        d = run_search(self.graph, 0, 99, "dijkstra")
        a = run_search(self.graph, 0, 99, "astar")
        # A* with an admissible heuristic must find the same optimal cost
        self.assertAlmostEqual(d["distance"], a["distance"], places=4)

    def test_astar_expands_fewer_or_equal_nodes(self):
        d = run_search(self.graph, 0, 99, "dijkstra")
        a = run_search(self.graph, 0, 99, "astar")
        # A* should never expand more nodes than Dijkstra when the
        # heuristic is admissible
        self.assertLessEqual(a["nodes_expanded"], d["nodes_expanded"])

    def test_path_starts_and_ends_correctly(self):
        result = run_search(self.graph, 0, 99, "dijkstra")
        self.assertEqual(result["path"][0], 0)
        self.assertEqual(result["path"][-1], 99)


if __name__ == "__main__":
    unittest.main()
