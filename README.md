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


## How to Run

Run the program from the command line:

```bash
python main.py p1_graph.txt
```

## Results and Discussion


**Experiment setup**
- Start node: `0` (Square 79)
- Destination node: `99` (Square 17)

**Observed output**

Calculating path from Node 0 (Sq: 79) to Node 99 (Sq: 17)...
```bash
Algorithm       | Cost       | Nodes Expanded  | Path Found
Dijkstra        | 6157.00    | 42              | Yes
A* (Star)       | 6157.00    | 11              | Yes
Path (Dijkstra): [0, 99]
```
**Analysis**

Both Dijkstra and A\* found the **same optimal path** with an identical total cost of **6157.00**, confirming that the heuristic used by A* is **admissible** and does not overestimate the true shortest-path cost.

However, there is a significant difference in search efficiency:

- **Dijkstra** expanded **42 nodes**, because it explores nodes uniformly outward from the start without any directional guidance.
- A* expanded only **11 nodes**, because the heuristic effectively guides the search toward the goal square by estimating a lower bound on the remaining distance.

The direct path `[0, 99]` indicates that a single edge connects the start and destination nodes, but Dijkstra still explored many alternative paths before confirming optimality. In contrast, A\* prioritized nodes closer to the goal (in terms of the heuristic), allowing it to reach the solution much faster.

**Conclusion**

This experiment shows that while both algorithms guarantee optimal solutions,
A* can be more efficient than Dijkstra when a well-designed admissible heuristic is available. The square-based Euclidean lower-bound heuristic significantly reduces the number of node expansions without sacrificing correctness.

