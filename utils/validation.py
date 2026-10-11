from __future__ import annotations
from typing import Any, List, Tuple, Optional


def validate_distance_matrix(matrix: Any) -> Tuple[bool, str, Optional[List[List[float]]]] :
    """
    Validate a distance matrix for an undirected TSP problem.
    
    Validation criteria:
    - Matrix must not be None or empty.
    - Matrix must be a 2D list or array-like structure.
    - Matrix must be square (n x n, with n >= 1).
    - All elements must be finite numbers (int or float).
    - All elements must be non-negative (>= 0).
    - Diagonal elements must be zero (matrix[i][i] == 0).
    - Matrix must be symmetric (matrix[i][j] == matrix[j][i]).
    
    Returns:
        (is_valid, error_message, validated_matrix_as_float)
    """
    if matrix is None:
        return False, "Distance matrix is None.", None

    if not isinstance(matrix, (list, tuple)):
        # Support numpy arrays if passed
        try:
            matrix = matrix.tolist()
        except AttributeError:
            return False, f"Expected list or 2D array, got {type(matrix).__name__}.", None

    n = len(matrix)
    if n == 0:
        return False, "Distance matrix is empty (0 cities).", None

    validated: List[List[float]] = []

    for i, row in enumerate(matrix):
        if not isinstance(row, (list, tuple)):
            try:
                row = row.tolist()
            except AttributeError:
                return False, f"Row {i} is not a valid sequence.", None

        if len(row) != n:
            return False, f"Distance matrix is non-square: row {i} has length {len(row)}, expected {n}.", None

        float_row: List[float] = []
        for j, val in enumerate(row):
            if val is None or isinstance(val, bool):
                return False, f"Element at ({i}, {j}) is not a valid number: {val}.", None
            try:
                num = float(val)
            except (ValueError, TypeError):
                return False, f"Element at ({i}, {j}) cannot be parsed as a float: {val}.", None

            if num < 0:
                return False, f"Distance at ({i}, {j}) is negative ({num}). All distances must be non-negative.", None

            float_row.append(num)
        validated.append(float_row)

    # Check zero diagonal
    for i in range(n):
        if abs(validated[i][i]) > 1e-9:
            return False, f"Diagonal element at ({i}, {i}) is non-zero ({validated[i][i]}). Must be 0.", None

    # Check symmetry
    for i in range(n):
        for j in range(i + 1, n):
            if abs(validated[i][j] - validated[j][i]) > 1e-6:
                return (
                    False,
                    f"Matrix is asymmetric: dist({i}, {j})={validated[i][j]} != dist({j}, {i})={validated[j][i]}.",
                    None
                )

    return True, "", validated


def validate_tour(tour: List[int], n: int, start_city: int = 0) -> Tuple[bool, str]:
    """
    Validate that a tour is a valid Travelling Salesperson tour of n cities.
    
    A valid tour must:
    - Start at start_city.
    - Visit every city in {0, ..., n-1} exactly once before returning to start_city.
    - For n >= 2: if tour has length n+1, it must end at start_city.
      If tour has length n, all n cities must be visited.
    - For n == 1: tour must visit city 0 (and optionally return to 0).
    """
    if not tour:
        return False, "Tour is empty."

    if n <= 0:
        return False, f"Invalid number of cities: {n}."

    if n == 1:
        if tour[0] != start_city:
            return False, f"Tour must start at city {start_city}, but starts at {tour[0]}."
        return True, ""

    if tour[0] != start_city:
        return False, f"Tour does not start at designated start city {start_city} (starts at {tour[0]})."

    # Normalize tour: if length is n+1 and ends at start_city, take tour[:-1]
    if len(tour) == n + 1:
        if tour[-1] != start_city:
            return False, f"Tour of length {n+1} does not return to start city {start_city} (ends at {tour[-1]})."
        visited = tour[:-1]
    elif len(tour) == n:
        visited = tour
    else:
        return False, f"Tour has invalid length {len(tour)}; expected {n} or {n+1} for {n} cities."

    # Check that visited cities are a permutation of 0..n-1
    if set(visited) != set(range(n)):
        missing = set(range(n)) - set(visited)
        duplicates = len(visited) - len(set(visited))
        msg = f"Tour does not visit every city exactly once."
        if missing:
            msg += f" Missing cities: {sorted(list(missing))}."
        if duplicates > 0:
            msg += f" Contains {duplicates} duplicate entries."
        return False, msg

    return True, ""


def check_metric_property(distance_matrix: List[List[float]]) -> Tuple[bool, str, Optional[Tuple[int, int, int]]]:
    """
    Check if a distance matrix satisfies the metric property (specifically the triangle inequality):
    d(i, k) <= d(i, j) + d(j, k) for all i, j, k.
    
    Returns:
        (is_metric, explanation_message, violating_triplet_if_any)
    """
    n = len(distance_matrix)
    tol = 1e-6
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if distance_matrix[i][k] > distance_matrix[i][j] + distance_matrix[j][k] + tol:
                    d_ik = distance_matrix[i][k]
                    sum_ij_jk = distance_matrix[i][j] + distance_matrix[j][k]
                    msg = (
                        f"Triangle inequality violated: d({i},{k})={d_ik:.4f} > "
                        f"d({i},{j}) + d({j},{k}) = {sum_ij_jk:.4f}."
                    )
                    return False, msg, (i, j, k)

    return True, "Distance matrix satisfies the triangle inequality (Metric TSP).", None
