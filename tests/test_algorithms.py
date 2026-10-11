from __future__ import annotations
import math
import pytest
from typing import List

from utils.distance import (
    euclidean_distance,
    generate_euclidean_cities,
    calculate_tour_cost,
    format_route,
)
from utils.validation import (
    validate_distance_matrix,
    validate_tour,
    check_metric_property,
)
from algorithms.brute_force import solve_tsp_brute_force
from algorithms.held_karp import solve_tsp_held_karp
from algorithms.nearest_neighbor import solve_tsp_nearest_neighbor
from algorithms.mst_approximation import solve_tsp_mst_approximation
from utils.benchmarking import run_benchmark_suite


class TestValidation:
    """Tests for distance matrix and tour validation functions."""

    def test_single_city_matrix(self):
        matrix = [[0.0]]
        valid, msg, val_mat = validate_distance_matrix(matrix)
        assert valid is True
        assert val_mat == [[0.0]]

    def test_valid_symmetric_matrix(self):
        matrix = [
            [0.0, 10.0, 15.0],
            [10.0, 0.0, 20.0],
            [15.0, 20.0, 0.0],
        ]
        valid, msg, val_mat = validate_distance_matrix(matrix)
        assert valid is True
        assert msg == ""
        assert len(val_mat) == 3

    def test_empty_matrix(self):
        valid, msg, val_mat = validate_distance_matrix([])
        assert valid is False
        assert "empty" in msg.lower()

    def test_non_square_matrix(self):
        matrix = [
            [0.0, 5.0, 10.0],
            [5.0, 0.0],
            [10.0, 5.0, 0.0],
        ]
        valid, msg, val_mat = validate_distance_matrix(matrix)
        assert valid is False
        assert "non-square" in msg.lower()

    def test_negative_distance(self):
        matrix = [
            [0.0, -5.0],
            [-5.0, 0.0],
        ]
        valid, msg, val_mat = validate_distance_matrix(matrix)
        assert valid is False
        assert "negative" in msg.lower()

    def test_non_zero_diagonal(self):
        matrix = [
            [2.0, 5.0],
            [5.0, 0.0],
        ]
        valid, msg, val_mat = validate_distance_matrix(matrix)
        assert valid is False
        assert "non-zero" in msg.lower()

    def test_asymmetric_matrix(self):
        matrix = [
            [0.0, 5.0, 10.0],
            [8.0, 0.0, 12.0],  # dist(1, 0) != dist(0, 1)
            [10.0, 12.0, 0.0],
        ]
        valid, msg, val_mat = validate_distance_matrix(matrix)
        assert valid is False
        assert "asymmetric" in msg.lower()

    def test_invalid_types_in_matrix(self):
        matrix = [
            [0.0, "invalid"],
            ["invalid", 0.0],
        ]
        valid, msg, val_mat = validate_distance_matrix(matrix)
        assert valid is False
        assert "cannot be parsed" in msg.lower()

    def test_validate_tour_valid(self):
        tour = [0, 2, 1, 3, 0]
        valid, msg = validate_tour(tour, n=4, start_city=0)
        assert valid is True

    def test_validate_tour_wrong_start(self):
        tour = [1, 2, 0, 3, 1]
        valid, msg = validate_tour(tour, n=4, start_city=0)
        assert valid is False
        assert "start city" in msg.lower()

    def test_validate_tour_missing_city(self):
        tour = [0, 1, 1, 3, 0]  # Missing city 2, duplicates city 1
        valid, msg = validate_tour(tour, n=4, start_city=0)
        assert valid is False
        assert "missing" in msg.lower() or "duplicate" in msg.lower()


class TestMetricCheck:
    """Tests for metric property verification."""

    def test_euclidean_satisfies_metric(self):
        _, _, matrix = generate_euclidean_cities(n=6, seed=42)
        is_metric, msg, triplet = check_metric_property(matrix)
        assert is_metric is True
        assert triplet is None

    def test_non_metric_matrix_detection(self):
        # Violation: d(0, 2) = 100 > d(0, 1) + d(1, 2) = 10 + 10 = 20
        matrix = [
            [0.0, 10.0, 100.0],
            [10.0, 0.0, 10.0],
            [100.0, 10.0, 0.0],
        ]
        is_metric, msg, triplet = check_metric_property(matrix)
        assert is_metric is False
        assert "violated" in msg.lower()
        assert triplet is not None


class TestAlgorithmsEdgeCases:
    """Tests for algorithm correctness on edge cases (n=1, n=2)."""

    def test_single_city(self):
        matrix = [[0.0]]
        for solver in [solve_tsp_brute_force, solve_tsp_held_karp, solve_tsp_nearest_neighbor, solve_tsp_mst_approximation]:
            tour, cost = solver(matrix, start_city=0)
            assert cost == 0.0
            assert tour[0] == 0
            assert validate_tour(tour, n=1, start_city=0)[0] is True

    def test_two_cities(self):
        matrix = [
            [0.0, 7.5],
            [7.5, 0.0],
        ]
        for solver in [solve_tsp_brute_force, solve_tsp_held_karp, solve_tsp_nearest_neighbor, solve_tsp_mst_approximation]:
            tour, cost = solver(matrix, start_city=0)
            assert cost == pytest.approx(15.0)
            assert tour == [0, 1, 0]
            valid, msg = validate_tour(tour, n=2, start_city=0)
            assert valid is True


class TestSmallKnownInstance:
    """Test with a textbook 4-city instance with known optimal cost."""

    @pytest.fixture
    def textbook_graph(self):
        # 4 cities:
        # dist matrix:
        # [0, 10, 15, 20]
        # [10, 0, 35, 25]
        # [15, 35, 0, 30]
        # [20, 25, 30, 0]
        # Possible tours from 0:
        # 0 - 1 - 2 - 3 - 0: 10 + 35 + 30 + 20 = 95
        # 0 - 1 - 3 - 2 - 0: 10 + 25 + 30 + 15 = 80  <-- OPTIMAL
        # 0 - 2 - 1 - 3 - 0: 15 + 35 + 25 + 20 = 95
        # 0 - 3 - 1 - 2 - 0: 20 + 25 + 35 + 15 = 95
        return [
            [0.0, 10.0, 15.0, 20.0],
            [10.0, 0.0, 35.0, 25.0],
            [15.0, 35.0, 0.0, 30.0],
            [20.0, 25.0, 30.0, 0.0],
        ]

    def test_exact_agreement(self, textbook_graph):
        tour_bf, cost_bf = solve_tsp_brute_force(textbook_graph, start_city=0)
        tour_hk, cost_hk = solve_tsp_held_karp(textbook_graph, start_city=0)

        assert cost_bf == pytest.approx(80.0)
        assert cost_hk == pytest.approx(80.0)
        assert cost_bf == cost_hk

        assert validate_tour(tour_bf, n=4, start_city=0)[0] is True
        assert validate_tour(tour_hk, n=4, start_city=0)[0] is True

    def test_nearest_neighbor(self, textbook_graph):
        tour_nn, cost_nn = solve_tsp_nearest_neighbor(textbook_graph, start_city=0)
        # From 0: nearest is 1 (cost 10)
        # From 1: unvisited are 2 (35), 3 (25) -> nearest is 3 (25)
        # From 3: unvisited is 2 (30) -> 2 (30)
        # From 2: return to 0 (15)
        # Total cost = 10 + 25 + 30 + 15 = 80
        assert validate_tour(tour_nn, n=4, start_city=0)[0] is True
        assert cost_nn >= 80.0

    def test_mst_approximation(self, textbook_graph):
        tour_mst, cost_mst = solve_tsp_mst_approximation(textbook_graph, start_city=0)
        assert validate_tour(tour_mst, n=4, start_city=0)[0] is True
        recalc = calculate_tour_cost(tour_mst, textbook_graph)
        assert cost_mst == pytest.approx(recalc)


class TestExactEquivalenceMultipleSeeds:
    """Verify that Brute Force and Held-Karp return identical optimal costs across various random instances."""

    @pytest.mark.parametrize("n_cities,seed", [
        (4, 101),
        (5, 202),
        (6, 303),
        (7, 404),
    ])
    def test_bf_hk_equivalence(self, n_cities, seed):
        _, _, matrix = generate_euclidean_cities(n=n_cities, seed=seed)
        
        tour_bf, cost_bf = solve_tsp_brute_force(matrix, start_city=0)
        tour_hk, cost_hk = solve_tsp_held_karp(matrix, start_city=0)

        # Both must return the exact same minimal cost
        assert cost_bf == pytest.approx(cost_hk, rel=1e-4)

        # Both tours must be valid Hamiltonian cycles
        assert validate_tour(tour_bf, n=n_cities, start_city=0)[0] is True
        assert validate_tour(tour_hk, n=n_cities, start_city=0)[0] is True

        # Independent calculation must match returned costs
        assert calculate_tour_cost(tour_bf, matrix) == pytest.approx(cost_bf, rel=1e-4)
        assert calculate_tour_cost(tour_hk, matrix) == pytest.approx(cost_hk, rel=1e-4)


class TestMetricApproximationRatio:
    """Verify that the MST 2-Approximation never exceeds 2 * OPT on metric instances."""

    @pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
    def test_mst_approximation_bound(self, seed):
        n_cities = 6
        _, _, matrix = generate_euclidean_cities(n=n_cities, seed=seed)

        # Find true optimal cost using Held-Karp
        _, opt_cost = solve_tsp_held_karp(matrix, start_city=0)

        # Run MST 2-approximation
        tour_mst, approx_cost = solve_tsp_mst_approximation(matrix, start_city=0)

        # Verification of 2-approximation bound: approx_cost <= 2.0 * opt_cost
        assert approx_cost <= 2.0 * opt_cost + 1e-4
        assert approx_cost >= opt_cost - 1e-4  # Cannot be better than optimal


class TestBenchmarkingSuite:
    """Test the full benchmark runner and metrics."""

    def test_benchmark_suite_execution(self):
        _, _, matrix = generate_euclidean_cities(n=5, seed=777)
        suite = run_benchmark_suite(
            distance_matrix=matrix,
            start_city=0,
            selected_algos=["brute_force", "held_karp", "nearest_neighbor", "mst_approximation"]
        )

        assert suite["city_count"] == 5
        assert suite["is_metric"] is True
        assert suite["optimal_cost"] is not None
        assert len(suite["results"]) == 4

        for res in suite["results"]:
            assert res.status == "Success"
            assert res.is_valid_route is True
            assert res.execution_time_sec >= 0.0
            assert res.cost == pytest.approx(res.recalculated_cost, rel=1e-4)
            assert res.optimality_gap_pct is not None
            assert res.optimality_gap_pct >= 0.0
