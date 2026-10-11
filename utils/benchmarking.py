from __future__ import annotations
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any, Callable

from .distance import calculate_tour_cost, format_route
from .validation import validate_tour, check_metric_property
from algorithms.brute_force import solve_tsp_brute_force
from algorithms.held_karp import solve_tsp_held_karp
from algorithms.nearest_neighbor import solve_tsp_nearest_neighbor
from algorithms.mst_approximation import solve_tsp_mst_approximation


# Recommended maximum safe inputs for educational UI execution
LIMIT_BRUTE_FORCE = 10
LIMIT_HELD_KARP = 18


@dataclass
class AlgorithmMetadata:
    key: str
    display_name: str
    category: str  # "Exact", "Heuristic", "Approximation"
    time_complexity: str
    space_complexity: str
    guarantee_text: str
    max_recommended_n: int
    solver_func: Callable[[List[List[float]], int], tuple]


ALGORITHM_REGISTRY: Dict[str, AlgorithmMetadata] = {
    "brute_force": AlgorithmMetadata(
        key="brute_force",
        display_name="Brute Force",
        category="Exact",
        time_complexity="O(n!)",
        space_complexity="O(n)",
        guarantee_text="Exact: Guaranteed Optimal",
        max_recommended_n=LIMIT_BRUTE_FORCE,
        solver_func=solve_tsp_brute_force,
    ),
    "held_karp": AlgorithmMetadata(
        key="held_karp",
        display_name="Held-Karp DP",
        category="Exact",
        time_complexity="O(n² · 2ⁿ)",
        space_complexity="O(n · 2ⁿ)",
        guarantee_text="Exact: Guaranteed Optimal",
        max_recommended_n=LIMIT_HELD_KARP,
        solver_func=solve_tsp_held_karp,
    ),
    "nearest_neighbor": AlgorithmMetadata(
        key="nearest_neighbor",
        display_name="Nearest Neighbor",
        category="Greedy Heuristic",
        time_complexity="O(n²)",
        space_complexity="O(n)",
        guarantee_text="Heuristic: No guarantee",
        max_recommended_n=2000,
        solver_func=solve_tsp_nearest_neighbor,
    ),
    "mst_approximation": AlgorithmMetadata(
        key="mst_approximation",
        display_name="MST 2-Approximation",
        category="Approximation",
        time_complexity="O(n²)",
        space_complexity="O(n)",
        guarantee_text="Approximation: ≤ 2× OPT (Metric TSP only)",
        max_recommended_n=2000,
        solver_func=solve_tsp_mst_approximation,
    ),
}


@dataclass
class BenchmarkResult:
    key: str
    display_name: str
    category: str
    time_complexity: str
    guarantee: str
    route: List[int]
    formatted_route: str
    cost: float
    recalculated_cost: float
    execution_time_sec: float
    is_valid_route: bool
    validation_message: str
    optimality_gap_pct: Optional[float]
    status: str  # "Success", "Skipped", "Error"
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_single_algorithm(
    algo_key: str,
    distance_matrix: List[List[float]],
    start_city: int = 0,
    city_names: Optional[List[str]] = None,
    optimal_cost: Optional[float] = None
) -> BenchmarkResult:
    """
    Run an individual TSP algorithm with precise high-resolution timing,
    route validation, independent cost calculation, and optimality gap reporting.
    """
    meta = ALGORITHM_REGISTRY[algo_key]
    n = len(distance_matrix)

    # Execute with high-resolution timer
    start_time = time.perf_counter()
    try:
        raw_tour, returned_cost = meta.solver_func(distance_matrix, start_city)
        elapsed_sec = time.perf_counter() - start_time
    except Exception as e:
        elapsed_sec = time.perf_counter() - start_time
        return BenchmarkResult(
            key=meta.key,
            display_name=meta.display_name,
            category=meta.category,
            time_complexity=meta.time_complexity,
            guarantee=meta.guarantee_text,
            route=[],
            formatted_route="Error",
            cost=0.0,
            recalculated_cost=0.0,
            execution_time_sec=elapsed_sec,
            is_valid_route=False,
            validation_message=str(e),
            optimality_gap_pct=None,
            status="Error",
            error_message=str(e),
        )

    # Validate route independently
    is_valid, val_msg = validate_tour(raw_tour, n, start_city)

    # Recalculate tour cost independently
    try:
        recalc_cost = calculate_tour_cost(raw_tour, distance_matrix)
    except Exception as e:
        recalc_cost = returned_cost
        val_msg += f" Cost recalculation error: {e}"

    # Calculate optimality gap if optimal_cost is provided
    gap_pct: Optional[float] = None
    if optimal_cost is not None and optimal_cost > 0.0:
        gap_pct = round(((recalc_cost - optimal_cost) / optimal_cost) * 100.0, 2)
    elif optimal_cost == 0.0:
        gap_pct = 0.0

    formatted = format_route(raw_tour, city_names)

    return BenchmarkResult(
        key=meta.key,
        display_name=meta.display_name,
        category=meta.category,
        time_complexity=meta.time_complexity,
        guarantee=meta.guarantee_text,
        route=raw_tour,
        formatted_route=formatted,
        cost=returned_cost,
        recalculated_cost=recalc_cost,
        execution_time_sec=elapsed_sec,
        is_valid_route=is_valid,
        validation_message=val_msg if val_msg else "Valid Hamiltonian Tour",
        optimality_gap_pct=gap_pct,
        status="Success" if is_valid else "Invalid Route",
        error_message=None if is_valid else val_msg,
    )


def run_benchmark_suite(
    distance_matrix: List[List[float]],
    start_city: int = 0,
    selected_algos: Optional[List[str]] = None,
    city_names: Optional[List[str]] = None,
    allow_large_exact: bool = False
) -> Dict[str, Any]:
    """
    Run the complete comparative benchmark across selected algorithms.
    Guarantees that every algorithm receives the exact same distance matrix
    and starting city.
    
    Determines true optimal cost from exact algorithms (Held-Karp or Brute Force)
    if they are executed, and subsequently computes the optimality gap.
    """
    n = len(distance_matrix)
    if selected_algos is None:
        selected_algos = list(ALGORITHM_REGISTRY.keys())

    is_metric, metric_msg, violating_triplet = check_metric_property(distance_matrix)

    results: List[BenchmarkResult] = []
    
    # Priority for determining optimal cost: Held-Karp, then Brute Force
    optimal_cost: Optional[float] = None

    # Step 1: Run exact algorithms first to establish reference optimum
    exact_keys = [k for k in ["held_karp", "brute_force"] if k in selected_algos]
    non_exact_keys = [k for k in selected_algos if k not in exact_keys]

    for key in exact_keys:
        meta = ALGORITHM_REGISTRY[key]
        if n > meta.max_recommended_n and not allow_large_exact:
            # Safely skip to protect application responsiveness
            results.append(
                BenchmarkResult(
                    key=meta.key,
                    display_name=meta.display_name,
                    category=meta.category,
                    time_complexity=meta.time_complexity,
                    guarantee=meta.guarantee_text,
                    route=[],
                    formatted_route="Skipped (n > limit)",
                    cost=0.0,
                    recalculated_cost=0.0,
                    execution_time_sec=0.0,
                    is_valid_route=False,
                    validation_message=f"Safety skip: n={n} exceeds safe limit of {meta.max_recommended_n}.",
                    optimality_gap_pct=None,
                    status="Skipped",
                    error_message=f"Instance size n={n} too large for practical exact execution.",
                )
            )
            continue

        res = run_single_algorithm(key, distance_matrix, start_city, city_names, optimal_cost=None)
        results.append(res)
        if res.status == "Success" and optimal_cost is None:
            optimal_cost = res.recalculated_cost

    # Step 2: Now run remaining algorithms (Heuristic & Approximation) with reference optimum
    for key in non_exact_keys:
        res = run_single_algorithm(key, distance_matrix, start_city, city_names, optimal_cost=optimal_cost)
        results.append(res)

    # Step 3: Backfill optimality gap for any exact solver that finished before optimal_cost was established
    for res in results:
        if res.status == "Success" and res.optimality_gap_pct is None and optimal_cost is not None:
            if optimal_cost > 0.0:
                res.optimality_gap_pct = round(((res.recalculated_cost - optimal_cost) / optimal_cost) * 100.0, 2)
            else:
                res.optimality_gap_pct = 0.0

    return {
        "city_count": n,
        "start_city": start_city,
        "is_metric": is_metric,
        "metric_message": metric_msg,
        "optimal_cost": optimal_cost,
        "results": results,
    }
