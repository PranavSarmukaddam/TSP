from __future__ import annotations
import os
import csv
import time
from typing import List, Dict, Any

from utils.distance import generate_euclidean_cities
from utils.benchmarking import run_benchmark_suite, LIMIT_BRUTE_FORCE, LIMIT_HELD_KARP


def run_comprehensive_benchmarks(
    city_counts: List[int] = [4, 6, 8, 10, 12, 14, 16],
    seed: int = 42,
    output_dir: str = "outputs"
) -> str:
    """
    Execute standardized experimental runs across multiple city counts,
    recording real execution times, tour costs, and optimality gaps.
    Saves results to a CSV file in output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "benchmark_results.csv")

    rows: List[Dict[str, Any]] = []

    print(f"\n================================================================================")
    print(f"  DAA TSP EXPERIMENTAL EVALUATION (Live High-Resolution Execution)")
    print(f"================================================================================")
    print(f"{'n':<4} | {'Algorithm':<20} | {'Cost':<10} | {'Time (ms)':<12} | {'Opt Gap (%)':<12} | {'Status':<10}")
    print(f"--------------------------------------------------------------------------------")

    for n in city_counts:
        city_names, coordinates, matrix = generate_euclidean_cities(n=n, seed=seed)

        # Decide which algorithms are safe to run
        algos_to_run = ["nearest_neighbor", "mst_approximation"]
        if n <= LIMIT_BRUTE_FORCE:
            algos_to_run.append("brute_force")
        if n <= LIMIT_HELD_KARP:
            algos_to_run.append("held_karp")

        suite = run_benchmark_suite(
            distance_matrix=matrix,
            start_city=0,
            selected_algos=algos_to_run,
            city_names=city_names
        )

        for res in suite["results"]:
            gap_str = f"{res.optimality_gap_pct:.2f}%" if res.optimality_gap_pct is not None else "N/A"
            time_ms = res.execution_time_sec * 1000.0

            print(f"{n:<4} | {res.display_name:<20} | {res.cost:<10.2f} | {time_ms:<12.3f} | {gap_str:<12} | {res.status:<10}")

            rows.append({
                "n_cities": n,
                "algorithm": res.display_name,
                "category": res.category,
                "complexity": res.time_complexity,
                "tour_cost": res.cost,
                "execution_time_ms": round(time_ms, 4),
                "execution_time_sec": round(res.execution_time_sec, 6),
                "optimality_gap_pct": gap_str,
                "status": res.status,
                "route": res.formatted_route
            })

    # Write to CSV
    fieldnames = [
        "n_cities", "algorithm", "category", "complexity", "tour_cost",
        "execution_time_ms", "execution_time_sec", "optimality_gap_pct", "status", "route"
    ]
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"--------------------------------------------------------------------------------")
    print(f"Saved benchmark results to {csv_path}\n")
    return csv_path


if __name__ == "__main__":
    run_comprehensive_benchmarks()
