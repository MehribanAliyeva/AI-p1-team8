# Shortest Path on a 10×10 Board: Dijkstra vs A*

This project compares **Dijkstra’s algorithm** and A* search on a weighted directed graph whose nodes are embedded in a 2D  structure. 
Each node lies somewhere inside a square of a 10×10 grid, but its exact coordinates are unknown. 
The goal is to find the shortest path between two nodes and to observe how an informed search (A\*) performs compared to an uninformed one (Dijkstra).

## Problem Description

The environment is a 10×10 “chessboard” consisting of 100 squares, indexed from 0 to 99 in row-major order.
Each square represents a 10×10 unit area. Nodes in the graph are assigned to squares, but their precise coordinates inside the square are not given.
Edges between nodes have weights that represent the Euclidean distance between the true coordinates of the endpoints.

Important geometric facts:
- Two points inside the same square can be at most √(10² + 10²) ≈ 14.1 units apart.
- Two points in adjacent squares can be arbitrarily close to each other.
- Only when squares are separated by at least one full square in between is there a guaranteed minimum distance.

## Heuristic Choice for A*

The heuristic is designed to be a **lower bound** on the true remaining path cost, using only square-level information. 
For a node in square `s` and a goal in square `g`, the algorithm:
- Converts square IDs into (row, column) positions on the 10×10 grid.
- Computes how many full squares must lie between the two squares in the vertical and horizontal directions.
- Assigns zero minimum distance for same or adjacent squares.
- Assigns a minimum forced distance of `(Δ − 1) × 10` units for each axis.
- Combines these minimum separations using Euclidean distance.
- Multiplies the result by 100 to match the scale of the edge weights.

Because this heuristic represents the **minimum possible Euclidean distance** between any two points in the two squares, and edge weights are Euclidean distances scaled by 100, the heuristic never overestimates the true shortest-path cost. 
Therefore, it is **admissible**, guaranteeing optimal paths when using A\*.

## Algorithm Comparison

The program runs both:
- **Dijkstra’s algorithm**, which does not use a heuristic and may expand many nodes.
- A* search, which uses the heuristic to guide the search toward the goal.

For each algorithm, the program reports:
- Whether a path was found
- Total path cost
- Number of nodes expanded
- Execution time (in milliseconds)
- Peak memory usage (in KB)


## How to Run

Run the program from the command line:

```bash
python main.py p1_graph.txt <start_node> <end_node>
```

If no start/end arguments are given, the program defaults to Node 0 → Node 50 (or uses values embedded in the graph file via `S,` and `D,` lines).

## Results and Discussion

Three experiments were run with different start/end pairs to evaluate the algorithms across a variety of scenarios.

---

### Experiment 1: Node 0 → Node 99

- Start node: `0` (Square 79)
- Destination node: `99` (Square 17)

```
Algorithm       | Cost       | Nodes Expanded  | Time (ms)    | Peak Mem (KB)  | Path Found
------------------------------------------------------------------------------------------
Dijkstra        | 6157.00    | 42              | 1.6461       | 13.80          | Yes
A* (Star)       | 6157.00    | 11              | 1.4809       | 7.22           | Yes

Path (Dijkstra): [0, 99]
Path (A*):       [0, 99]
```

The direct edge `0 → 99` happens to be the shortest path. Despite this, Dijkstra expanded **42 nodes** before confirming optimality, while A\* reached the goal after only **11 expansions** by using the heuristic to deprioritize distant squares.

---

### Experiment 2: Node 1 → Node 50

- Start node: `1` (Square 28)
- Destination node: `50` (Square 77)

```
Algorithm       | Cost       | Nodes Expanded  | Time (ms)    | Peak Mem (KB)  | Path Found
------------------------------------------------------------------------------------------
Dijkstra        | 9223.00    | 51              | 1.3064       | 12.71          | Yes
A* (Star)       | 9223.00    | 19              | 1.1427       | 7.79           | Yes

Path (Dijkstra): [1, 29, 50]
Path (A*):       [1, 29, 50]
```

A two-hop path through Node 29 is optimal. Dijkstra expanded **51 nodes** — more than half the graph — compared to A\*'s **19**. The heuristic correctly steered the search toward the lower-right region of the board (Square 77), cutting exploration by over 60%.

---

### Experiment 3: Node 10 → Node 95

- Start node: `10` (Square 8)
- Destination node: `95` (Square 20)

```
Algorithm       | Cost       | Nodes Expanded  | Time (ms)    | Peak Mem (KB)  | Path Found
------------------------------------------------------------------------------------------
Dijkstra        | 9027.00    | 40              | 1.2109       | 12.42          | Yes
A* (Star)       | 9027.00    | 10              | 0.7392       | 6.45           | Yes

Path (Dijkstra): [10, 26, 95]
Path (A*):       [10, 26, 95]
```

This is the strongest demonstration of A\*'s advantage: it expanded only **10 nodes** compared to Dijkstra's **40** — a **4× reduction**. The start and goal squares are both in the top three rows of the board, so the heuristic heavily penalized nodes in faraway squares, pruning most of the search space.

---

## Summary Table

| Experiment | Start → End | Cost      | Dijkstra Expanded | A\* Expanded | Reduction |
|------------|-------------|-----------|-------------------|--------------|-----------|
| 1          | 0 → 99      | 6157.00   | 42                | 11           | 73.8%     |
| 2          | 1 → 50      | 9223.00   | 51                | 19           | 62.7%     |
| 3          | 10 → 95     | 9027.00   | 40                | 10           | 75.0%     |

## Conclusion

Across all three experiments, Dijkstra and A\* found the **same optimal paths** with **identical costs**, confirming that the heuristic is **admissible** and does not compromise correctness.

However, A\* consistently expanded **60–75% fewer nodes** than Dijkstra. This translates into measurably lower peak memory usage (typically 30–50% less) and, in most cases, faster execution times. The advantage is most pronounced when the start and goal are in nearby regions of the board, because the heuristic can aggressively deprioritize nodes in distant squares.

These results demonstrate that even a coarse heuristic, which only knows which 10×10 square a node belongs to, not its exact coordinates, provides substantial search efficiency gains when paired with A\*.
