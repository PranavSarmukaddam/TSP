from __future__ import annotations
import itertools
from typing import List, Tuple


def solve_tsp_brute_force(
    distance_matrix: List[List[float]],
    start_city: int = 0
) -> Tuple[List[int], float]:
    """
    Exact TSP solver using Brute Force permutation search.
    
    Fixes the starting city to avoid evaluating cyclic shifts of identical tours.
    Generates all (n - 1)! permutations of the remaining cities and tracks
    the tour with minimum total travel cost.
    
    Time Complexity: O(n!) - specifically O((n - 1)! * n) operations.
    Space Complexity: O(n) to store candidate and best tours.
    Optimality: Exact (guaranteed optimal tour).
    Practical limit: Small n only (typically n <= 10).
    
    Parameters:
        distance_matrix: n x n symmetric matrix of distances.
        start_city: 0-indexed city to start and end the tour at.
        
    Returns:
        (best_tour, best_cost):
            best_tour: list of city indices visited, ending at start_city.
            best_cost: total distance of the optimal tour.
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

    remaining_cities = [c for c in range(n) if c != start_city]
    best_tour: List[int] = []
    best_cost = float("inf")

    for perm in itertools.permutations(remaining_cities):
        # Construct candidate tour: start -> perm[0] -> ... -> perm[-1] -> start
        current_cost = 0.0
        prev = start_city
        for city in perm:
            current_cost += distance_matrix[prev][city]
            prev = city
        current_cost += distance_matrix[prev][start_city]

        if current_cost < best_cost:
            best_cost = current_cost
            best_tour = [start_city] + list(perm) + [start_city]

    return best_tour, round(best_cost, 4)
