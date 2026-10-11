from __future__ import annotations
from typing import List, Tuple, Dict, Set


def compute_mst_prim(
    distance_matrix: List[List[float]],
    start_city: int = 0
) -> List[Tuple[int, int, float]]:
    """
    Compute Minimum Spanning Tree (MST) using Prim's algorithm on an n x n complete graph.
    
    Time Complexity: O(n^2) dense graph implementation.
    Returns:
        List of undirected edges as (u, v, weight).
    """
    n = len(distance_matrix)
    if n <= 1:
        return []

    in_mst = [False] * n
    min_edge = [float("inf")] * n
    parent = [-1] * n

    min_edge[start_city] = 0.0

    for _ in range(n):
        # Pick vertex not in MST with smallest min_edge
        u = -1
        best_val = float("inf")
        for i in range(n):
            if not in_mst[i] and min_edge[i] < best_val:
                best_val = min_edge[i]
                u = i

        if u == -1:
            break

        in_mst[u] = True

        # Relax edges from u to all unvisited vertices
        for v in range(n):
            if not in_mst[v] and distance_matrix[u][v] < min_edge[v]:
                min_edge[v] = distance_matrix[u][v]
                parent[v] = u

    mst_edges: List[Tuple[int, int, float]] = []
    for v in range(n):
        if v != start_city and parent[v] != -1:
            u = parent[v]
            mst_edges.append((min(u, v), max(u, v), distance_matrix[u][v]))

    return mst_edges


def solve_tsp_mst_approximation(
    distance_matrix: List[List[float]],
    start_city: int = 0
) -> Tuple[List[int], float]:
    """
    Metric-TSP 2-Approximation algorithm using Minimum Spanning Tree (MST)
    and preorder tree traversal with shortcutting.
    
    Theoretical Guarantee:
        Approximation Ratio: <= 2 * OPT (Tour cost is guaranteed to be within
        twice the optimal tour cost), PROVIDED the distance metric satisfies
        the triangle inequality: d(u, w) <= d(u, v) + d(v, w).
        
        Important: If the triangle inequality is violated (non-metric TSP),
        shortcutting may increase edge costs and the 2-approximation bound
        DOES NOT apply.
        
    Algorithm Steps:
        1. Construct the Minimum Spanning Tree (MST) of the complete graph
           using Prim's Algorithm (Cost(MST) < Cost(OPT_TSP)).
        2. Double the MST edges to form an Eulerian multigraph (Cost <= 2 * Cost(MST)).
        3. Traverse the tree starting from `start_city` in Preorder / Depth-First Search.
        4. Shortcut duplicate city visits by skipping already-visited vertices
           (By triangle inequality, direct shortcut edge <= intermediate path).
        5. Return to `start_city` to form a complete Hamiltonian cycle.
        
    Time Complexity: O(n^2) for dense distance matrices.
    Space Complexity: O(n) for adjacency list, visited tracking, and route.
    
    Parameters:
        distance_matrix: n x n symmetric matrix of distances.
        start_city: 0-indexed city to start and end the tour at.
        
    Returns:
        (tour, cost):
            tour: list of city indices visited, ending at start_city.
            cost: total distance of the approximation tour.
    """
    n = len(distance_matrix)
    if n == 0:
        return [], 0.0
    if n == 1:
        return [start_city, start_city], 0.0
    if n == 2:
        other_city = 1 if start_city == 0 else 0
        tour = [start_city, other_city, start_city]
        cost = round(distance_matrix[start_city][other_city] + distance_matrix[other_city][start_city], 4)
        return tour, cost

    mst_edges = compute_mst_prim(distance_matrix, start_city)

    # Build adjacency list from MST edges
    adj: Dict[int, List[int]] = {i: [] for i in range(n)}
    for u, v, _ in mst_edges:
        adj[u].append(v)
        adj[v].append(u)

    # Sort neighbors for deterministic preorder traversal
    for i in range(n):
        adj[i].sort()

    # Preorder / DFS traversal with shortcutting
    tour: List[int] = []
    visited: Set[int] = set()

    def dfs(u: int) -> None:
        visited.add(u)
        tour.append(u)
        for neighbor in adj[u]:
            if neighbor not in visited:
                dfs(neighbor)

    dfs(start_city)

    # Complete the tour by returning to start_city
    tour.append(start_city)

    # Calculate total tour cost
    total_cost = 0.0
    for i in range(len(tour) - 1):
        u, v = tour[i], tour[i + 1]
        total_cost += distance_matrix[u][v]

    return tour, round(total_cost, 4)
