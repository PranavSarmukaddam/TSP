from __future__ import annotations
import math
import random
from typing import List, Tuple, Optional


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean (straight-line) distance between two 2D points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def city_names_for_count(n: int) -> List[str]:
    """Generate human-friendly city labels: A, B, ..., Z, AA, AB, etc."""
    names: List[str] = []
    for i in range(n):
        label = ""
        temp = i
        while True:
            label = chr(65 + (temp % 26)) + label
            temp = (temp // 26) - 1
            if temp < 0:
                break
        names.append(label)
    return names


def generate_euclidean_cities(
    n: int,
    seed: Optional[int] = None,
    width: float = 100.0,
    height: float = 100.0,
    round_decimals: int = 2
) -> Tuple[List[str], List[Tuple[float, float]], List[List[float]]]:
    """
    Generate reproducible random 2D city coordinates and the corresponding
    symmetric Euclidean distance matrix.
    
    Returns:
        city_names: List of string labels for each city.
        coordinates: List of (x, y) coordinates.
        distance_matrix: Symmetric n x n distance matrix.
    """
    if n <= 0:
        raise ValueError("Number of cities must be positive.")

    rng = random.Random(seed)
    coordinates: List[Tuple[float, float]] = []
    for _ in range(n):
        x = round(rng.uniform(5.0, width - 5.0), round_decimals)
        y = round(rng.uniform(5.0, height - 5.0), round_decimals)
        coordinates.append((x, y))

    city_names = city_names_for_count(n)

    # Build symmetric distance matrix
    matrix: List[List[float]] = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dist = round(euclidean_distance(coordinates[i], coordinates[j]), round_decimals)
            matrix[i][j] = dist
            matrix[j][i] = dist

    return city_names, coordinates, matrix


def calculate_tour_cost(tour: List[int], distance_matrix: List[List[float]]) -> float:
    """
    Independently calculate the total cost of a tour.
    
    A tour is assumed to be a sequence of city indices.
    If the tour has length n and does not explicitly end with the start city,
    the return edge (tour[-1] -> tour[0]) is automatically added.
    If the tour already has length n + 1 and ends with tour[0], it sums all adjacent edges.
    """
    if not tour:
        return 0.0
    if len(tour) == 1:
        return 0.0

    n = len(distance_matrix)
    # Validate indices exist in distance matrix
    for idx in tour:
        if idx < 0 or idx >= n:
            raise IndexError(f"City index {idx} out of range for matrix of size {n}.")

    total_cost = 0.0
    for i in range(len(tour) - 1):
        u, v = tour[i], tour[i + 1]
        total_cost += distance_matrix[u][v]

    # If tour does not explicitly loop back to start, add the return leg
    if tour[0] != tour[-1]:
        total_cost += distance_matrix[tour[-1]][tour[0]]

    return round(total_cost, 4)


def format_route(tour: List[int], city_names: Optional[List[str]] = None) -> str:
    """
    Format a tour as a human-readable string: e.g., 'A → C → B → D → A'.
    Ensures the final return to the start city is shown.
    """
    if not tour:
        return "Empty tour"

    display_tour = list(tour)
    if len(display_tour) > 1 and display_tour[0] != display_tour[-1]:
        display_tour.append(display_tour[0])

    if city_names is not None:
        labels = [city_names[i] if 0 <= i < len(city_names) else f"City_{i}" for i in display_tour]
    else:
        labels = [str(i) for i in display_tour]

    return " → ".join(labels)
