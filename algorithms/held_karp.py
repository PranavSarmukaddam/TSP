from __future__ import annotations
import itertools
from typing import List, Tuple, Dict, Optional


def solve_tsp_held_karp(
    distance_matrix: List[List[float]],
    start_city: int = 0
) -> Tuple[List[int], float]:
    r"""
    Exact TSP solver using the Held-Karp dynamic programming algorithm.
    
    Subproblem definition:
        memo[(mask, u)] = (cost, parent)
        where `mask` is a bitmask of visited cities (start_city is always visited),
        and `u` is the current end city of the path.
        The value is the minimum cost to start at `start_city`, visit all cities
        in `mask`, and end at `u`.
        
    Transitions:
        memo[(mask, u)] = min over v in (mask \ {u}) of:
            memo[(mask \ {u}, v)] + distance_matrix[v][u]
            
    Tour completion:
        optimal_cost = min over u != start_city of:
            memo[(full_mask, u)] + distance_matrix[u][start_city]
            
    Time Complexity: O(n^2 * 2^n) operations.
    Space Complexity: O(n * 2^n) memory states.
    Optimality: Exact (guaranteed optimal tour).
    Practical limit: Moderate n (typically n <= 18-20).
    
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

    # memo maps (bitmask, current_end_node) -> (min_cost, parent_node)
    memo: Dict[Tuple[int, int], Tuple[float, Optional[int]]] = {}
    
    # Base case: only start_city is visited
    start_mask = 1 << start_city
    memo[(start_mask, start_city)] = (0.0, None)

    other_cities = [c for c in range(n) if c != start_city]

    # Iterate over subset sizes from 2 to n (including start_city)
    for subset_size in range(2, n + 1):
        for combo in itertools.combinations(other_cities, subset_size - 1):
            mask = start_mask
            for c in combo:
                mask |= (1 << c)

            for u in combo:
                prev_mask = mask ^ (1 << u)
                best_cost = float("inf")
                best_parent: Optional[int] = None

                # Possible previous vertices v in prev_mask
                if subset_size == 2:
                    # Previous vertex must be start_city
                    cand_cost = memo[(prev_mask, start_city)][0] + distance_matrix[start_city][u]
                    best_cost = cand_cost
                    best_parent = start_city
                else:
                    for v in combo:
                        if v != u and (prev_mask, v) in memo:
                            cand_cost = memo[(prev_mask, v)][0] + distance_matrix[v][u]
                            if cand_cost < best_cost:
                                best_cost = cand_cost
                                best_parent = v

                memo[(mask, u)] = (best_cost, best_parent)

    # Close the cycle: return to start_city from the last city
    full_mask = (1 << n) - 1
    best_total_cost = float("inf")
    best_last_city: Optional[int] = None

    for u in other_cities:
        if (full_mask, u) in memo:
            tour_cost = memo[(full_mask, u)][0] + distance_matrix[u][start_city]
            if tour_cost < best_total_cost:
                best_total_cost = tour_cost
                best_last_city = u

    # Reconstruct optimal tour by backtracking
    if best_last_city is None:
        return [], float("inf")

    path: List[int] = []
    curr_city: Optional[int] = best_last_city
    curr_mask = full_mask

    while curr_city is not None:
        path.append(curr_city)
        _, parent = memo[(curr_mask, curr_city)]
        curr_mask = curr_mask ^ (1 << curr_city)
        curr_city = parent

    path.reverse()  # Now starts with start_city and ends with best_last_city
    full_tour = path + [start_city]

    return full_tour, round(best_total_cost, 4)
