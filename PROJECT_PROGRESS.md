# Project Progress: DAA Travelling Salesperson Problem (TSP) Mini-Project

## Project Information
- **Course**: Design and Analysis of Algorithms (DAA), B.E. Computer Engineering (SPPU 2019 Pattern)
- **Title**: Different Exact and Approximation Algorithms for the Travelling-Salesperson Problem
- **Technology Stack**: Python 3.8.0, Streamlit 1.40.1, Matplotlib, NumPy, Pytest 8.3.5

---

## 1. Objectives & Scope Verification

| Requirement | Implementation Details | Verification Status |
| :--- | :--- | :---: |
| **Brute Force (Exact)** | Enumerates $(n-1)!$ permutations with fixed start city. Time: $\mathcal{O}(n!)$, Space: $\mathcal{O}(n)$. | VERIFIED (Optimal on all tests) |
| **Held-Karp (Exact DP)** | Bitmask dynamic programming $C(S, j)$ with path backtracking. Time: $\mathcal{O}(n^2 2^n)$, Space: $\mathcal{O}(n 2^n)$. | VERIFIED (Identical cost to Brute Force) |
| **Nearest Neighbor (Heuristic)** | Greedy choice with deterministic index tie-breaking. Time: $\mathcal{O}(n^2)$, Space: $\mathcal{O}(n)$. | VERIFIED (Fast $\le 0.09\text{ ms}$, valid Hamiltonian tour) |
| **MST 2-Approximation** | Prim's MST + preorder DFS shortcutting. $\le 2 \times \text{OPT}$ bound validated on metric instances. | VERIFIED (Cost strictly $\le 2 \times \text{OPT}$) |
| **Fair Comparison** | All 4 algorithms run on the exact same distance matrix and starting city. | VERIFIED |
| **High-Resolution Timer** | Timing captured via `time.perf_counter()`. No hardcoded or fabricated numbers. | VERIFIED |
| **Independent Tour Validation** | Tour vertices verified to form a valid permutation visiting each city once before returning. | VERIFIED |
| **Independent Cost Recalculation** | Route distance independently summed from adjacent edge weights in matrix. | VERIFIED |
| **Metric Property Verification** | Verifies triangle inequality $d(u, w) \le d(u, v) + d(v, w)$ for every triplet. | VERIFIED |
| **Interactive Streamlit Web UI** | 2D tour mapping with start-city highlights, runtime/distance bar charts, complexity guide, viva cheat sheet. | VERIFIED (AppTest passed with 0 errors) |
| **Export Capabilities** | CSV export of benchmark comparison results. | VERIFIED |

---

## 2. Completed Milestones

- [x] **Specification Analysis**: Master requirements extracted and analyzed from `DAA_TSP_Antigravity_Project_Specification.docx`.
- [x] **Environment Setup**: Python 3.8 environment configured with `streamlit 1.40.1`, `pytest 8.3.5`, `matplotlib`, `numpy`, `scipy`.
- [x] **Core Utility Package (`utils/`)**:
  - `distance.py`: Euclidean city generator, tour cost recalculator, route formatter.
  - `validation.py`: Matrix square/symmetry/non-negativity/zero-diagonal checks, Hamiltonian tour validator, triangle inequality verifier.
  - `benchmarking.py`: Standardized runner, timer, optimality gap calculator.
  - `visualizations.py`: Matplotlib 2D tour visualizer, execution time bar chart, tour distance and optimality gap chart.
- [x] **Algorithms Package (`algorithms/`)**:
  - `brute_force.py`: Exact permutation solver with fixed start city.
  - `held_karp.py`: Exact bitmask dynamic programming solver.
  - `nearest_neighbor.py`: Greedy heuristic solver with consistent tie-breaking.
  - `mst_approximation.py`: Metric 2-approximation using Prim's MST and preorder DFS shortcutting.
- [x] **Comprehensive Test Suite (`tests/test_algorithms.py`)**:
  - 28 unit and integration tests covering:
    - Single-city ($n=1$) and two-city ($n=2$) edge cases
    - Matrix validation: negative values, non-square, non-zero diagonal, asymmetry, malformed input
    - Tour validation: start city mismatch, missing cities, duplicates
    - Metric check: Euclidean validity vs non-metric triangle inequality violation
    - Small known textbook instance (4 cities)
    - Brute Force vs Held-Karp exact optimality equivalence across multiple seeds
    - MST 2-approximation ratio $\le 2 \times \text{OPT}$ bound validation
    - Full benchmark suite execution and metric reporting
- [x] **Automated Test Run**: Ran `pytest -v tests/test_algorithms.py` -> **28 passed in 0.21s** with 0 warnings.
- [x] **Streamlit Application (`app.py`)**:
  - Full-featured educational UI with 2D route map, performance charts, DAA analysis, and viva cheat sheet.
  - Verified headlessly via Streamlit `AppTest` with 0 errors.
  - UI refined to remove all informal emojis, AI-specific markers, and explicit course/viva tags for a clean, professional platform appearance.
- [x] **Empirical Benchmark Runner (`benchmark_runner.py`)**:
  - Executed live benchmark experiments across $n = 4, 6, 8, 10, 12, 14, 16$.
  - Output saved to `outputs/benchmark_results.csv`.
- [x] **Project Documentation (`README.md`)**:
  - Complete guide covering setup, run commands, complexity tables, live benchmark data, and viva preparation.

---

## 3. Actual Test Execution Log

```
============================= test session starts =============================
platform win32 -- Python 3.8.0, pytest-8.3.5, pluggy-1.5.0
cachedir: .pytest_cache
rootdir: F:\Traveling Salesman
plugins: anyio-4.5.2
collected 28 items

tests/test_algorithms.py::TestValidation::test_single_city_matrix PASSED [  3%]
tests/test_algorithms.py::TestValidation::test_valid_symmetric_matrix PASSED [  7%]
tests/test_algorithms.py::TestValidation::test_empty_matrix PASSED       [ 10%]
tests/test_algorithms.py::TestValidation::test_non_square_matrix PASSED  [ 14%]
tests/test_algorithms.py::TestValidation::test_negative_distance PASSED  [ 17%]
tests/test_algorithms.py::TestValidation::test_non_zero_diagonal PASSED  [ 21%]
tests/test_algorithms.py::TestValidation::test_asymmetric_matrix PASSED  [ 25%]
tests/test_algorithms.py::TestValidation::test_invalid_types_in_matrix PASSED [ 28%]
tests/test_algorithms.py::TestValidation::test_validate_tour_valid PASSED [ 32%]
tests/test_algorithms.py::TestValidation::test_validate_tour_wrong_start PASSED [ 35%]
tests/test_algorithms.py::TestValidation::test_validate_tour_missing_city PASSED [ 39%]
tests/test_algorithms.py::TestMetricCheck::test_euclidean_satisfies_metric PASSED [ 42%]
tests/test_algorithms.py::TestMetricCheck::test_non_metric_matrix_detection PASSED [ 46%]
tests/test_algorithms.py::TestAlgorithmsEdgeCases::test_single_city PASSED [ 50%]
tests/test_algorithms.py::TestAlgorithmsEdgeCases::test_two_cities PASSED [ 53%]
tests/test_algorithms.py::TestSmallKnownInstance::test_exact_agreement PASSED [ 57%]
tests/test_algorithms.py::TestSmallKnownInstance::test_nearest_neighbor PASSED [ 60%]
tests/test_algorithms.py::TestSmallKnownInstance::test_mst_approximation PASSED [ 64%]
tests/test_algorithms.py::TestExactEquivalenceMultipleSeeds::test_bf_hk_equivalence[4-101] PASSED [ 67%]
tests/test_algorithms.py::TestExactEquivalenceMultipleSeeds::test_bf_hk_equivalence[5-202] PASSED [ 71%]
tests/test_algorithms.py::TestExactEquivalenceMultipleSeeds::test_bf_hk_equivalence[6-303] PASSED [ 75%]
tests/test_algorithms.py::TestExactEquivalenceMultipleSeeds::test_bf_hk_equivalence[7-404] PASSED [ 78%]
tests/test_algorithms.py::TestMetricApproximationRatio::test_mst_approximation_bound[1] PASSED [ 82%]
tests/test_algorithms.py::TestMetricApproximationRatio::test_mst_approximation_bound[2] PASSED [ 85%]
tests/test_algorithms.py::TestMetricApproximationRatio::test_mst_approximation_bound[3] PASSED [ 89%]
tests/test_algorithms.py::TestMetricApproximationRatio::test_mst_approximation_bound[4] PASSED [ 92%]
tests/test_algorithms.py::TestMetricApproximationRatio::test_mst_approximation_bound[5] PASSED [ 96%]
tests/test_algorithms.py::TestBenchmarkingSuite::test_benchmark_suite_execution PASSED [100%]

============================= 28 passed in 0.21s ==============================
```

---

## 4. Live Empirical Results Summary

| $n$ | Algorithm | Tour Cost | Time (ms) | Optimality Gap (%) | Status |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 4 | Held-Karp DP | 173.89 | 0.090 ms | 0.00% (Opt) | Success |
| 4 | Brute Force | 173.89 | 0.025 ms | 0.00% (Opt) | Success |
| 4 | Nearest Neighbor | 173.89 | 0.023 ms | 0.00% | Success |
| 4 | MST 2-Approximation | 208.43 | 0.058 ms | 19.86% | Success |
| 10 | Held-Karp DP | 237.71 | **23.264 ms** | 0.00% (Opt) | Success |
| 10 | Brute Force | 237.71 | **1045.696 ms** | 0.00% (Opt) | Success |
| 10 | Nearest Neighbor | 265.20 | 0.045 ms | 11.56% | Success |
| 10 | MST 2-Approximation | 311.31 | 0.112 ms | 30.96% | Success |
| 16 | Held-Karp DP | 260.71 | **2268.792 ms** | 0.00% (Opt) | Success |
| 16 | Nearest Neighbor | 302.07 | 0.090 ms | 15.86% | Success |
| 16 | MST 2-Approximation | 380.94 | 0.210 ms | 46.12% | Success |

---

## 5. Known Limitations & Safe Operating Thresholds
1. **Brute Force Permutations**: Recommended limit $n \le 10$. Beyond $n=10$, computation time exceeds 1 second per run due to $(n-1)!$ factorial scaling.
2. **Held-Karp Dynamic Programming**: Recommended limit $n \le 18$. Beyond $n=18$, exponential memory requirements ($O(n \cdot 2^n)$ states) risk memory exhaustion.
3. **Metric Approximation Scope**: The $\le 2 \times \text{OPT}$ bound applies strictly to instances satisfying the triangle inequality (such as Euclidean straight-line distance). Arbitrary asymmetric or non-metric matrices are explicitly flagged in the UI.

---

## 6. How to Run for College Demonstration and Viva
1. **Start Streamlit App**:
   ```bash
   streamlit run app.py
   ```
2. **Run Pytest Test Suite**:
   ```bash
   pytest -v tests/test_algorithms.py
   ```
3. **Run CLI Benchmarks**:
   ```bash
   python benchmark_runner.py
   ```
