from __future__ import annotations
from typing import List, Tuple


def solve_tsp_nearest_neighbor(
    distance_matrix: List[List[float]],
    start_city: int = 0
) -> Tuple[List[int], float]:
    """
    Greedy heuristic TSP solver using the Nearest Neighbor algorithm.
    
    Starting at `start_city`, repeatedly selects the nearest unvisited city.
    When multiple unvisited cities are equidistant, uses the consistent
    tie-breaking rule of choosing the city with the lowest numeric index.
    After visiting all cities, returns to `start_city`.
    
    Time Complexity: O(n^2) when scanning an n x n distance matrix.
    Space Complexity: O(n) to maintain visited set and route.
    Optimality: Heuristic (NO guarantee of optimality, and NO constant-factor
                approximation bound in general). The route quality is sensitive
                to the choice of start city.
                
    Parameters:
        distance_matrix: n x n symmetric matrix of distances.
        start_city: 0-indexed city to start and end the tour at.
        
    Returns:
        (tour, cost):
            tour: list of city indices visited, ending at start_city.
            cost: total distance of the heuristic tour.
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

    tour = [start_city]
    visited = {start_city}
    current_city = start_city
    total_cost = 0.0

    while len(visited) < n:
        best_next: int = -1
        min_dist = float("inf")

        for cand in range(n):
            if cand not in visited:
                d = distance_matrix[current_city][cand]
                # Consistent tie-breaking: prefer strictly smaller distance,
                # or lower candidate index on equal distance
                if d < min_dist:
                    min_dist = d
                    best_next = cand
                elif d == min_dist and cand < best_next:
                    best_next = cand

        tour.append(best_next)
        visited.add(best_next)
        total_cost += min_dist
        current_city = best_next

    # Return to start city
    return_dist = distance_matrix[current_city][start_city]
    tour.append(start_city)
    total_cost += return_dist

    return tour, round(total_cost, 4)
