# Different Exact and Approximation Algorithms for the Travelling-Salesperson Problem

[![Course](https://img.shields.io/badge/Course-Design%20%26%20Analysis%20of%20Algorithms%20(DAA)-blue.svg)]()
[![Pattern](https://img.shields.io/badge/Curriculum-SPPU%202019%20Pattern-orange.svg)]()
[![Degree](https://img.shields.io/badge/Degree-B.E.%20Computer%20Engineering-green.svg)]()
[![Tests](https://img.shields.io/badge/Tests-28%20Passed-brightgreen.svg)]()

A comprehensive, interactive educational software and comparative analysis system developed for the **Design and Analysis of Algorithms (DAA)** laboratory curriculum. This project implements, tests, visualizes, and rigorously benchmarks four distinct algorithmic approaches to the **Travelling Salesperson Problem (TSP)** on identical problem instances.

---

## 1. Project Overview & Problem Statement

Given a list of $n$ cities and pairwise travel distances, the **Travelling Salesperson Problem (TSP)** asks for the minimum-cost Hamiltonian cycle: a tour that visits every city exactly once and returns to the starting origin.

TSP is a canonical **NP-hard** combinatorial optimization problem. This project demonstrates how algorithm design paradigms (Exhaustive Search, Dynamic Programming, Greedy Heuristics, and Minimum Spanning Tree Tree-Based Approximation) trade off **optimality**, **execution speed**, and **memory scalability**.

---

## 2. Implemented Algorithms

| Algorithm | Paradigm | Time Complexity | Space Complexity | Optimality Guarantee | Practical Input Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Brute Force** | Exhaustive Search | $\mathcal{O}((n-1)! \cdot n) = \mathcal{O}(n!)$ | $\mathcal{O}(n)$ | **Exact**: Guaranteed 100% Optimal | $n \le 10$ |
| **Held-Karp** | Dynamic Programming (Bitmask) | $\mathcal{O}(n^2 \cdot 2^n)$ | $\mathcal{O}(n \cdot 2^n)$ | **Exact**: Guaranteed 100% Optimal | $n \le 18$ |
| **Nearest Neighbor** | Greedy Heuristic | $\mathcal{O}(n^2)$ | $\mathcal{O}(n)$ | **Heuristic**: No guarantee (Can be $> 2 \times \text{OPT}$) | $n \le 2000+$ |
| **MST 2-Approximation** | Metric Approximation | $\mathcal{O}(n^2)$ | $\mathcal{O}(n)$ | **Approximation**: $\le 2 \times \text{OPT}$ (Metric TSP only) | $n \le 2000+$ |

### Detailed Algorithm Descriptions

#### 1. Brute Force (`algorithms/brute_force.py`)
- **Strategy**: Fixes the starting city (to break rotational symmetry) and enumerates all $(n - 1)!$ permutations of remaining cities.
- **Role**: Serves as the ground-truth baseline for small instances.
- **Limitation**: Suffers from factorial growth ($10! \approx 3.6 \times 10^6$ tours, $15! \approx 1.3 \times 10^{12}$ tours).

#### 2. Held-Karp Dynamic Programming (`algorithms/held_karp.py`)
- **Strategy**: Utilizes Bellman-Held-Karp subset dynamic programming.
- **Recurrence**:
  Let $C(S, j)$ be the minimum path cost starting at $s$, visiting all vertices in subset $S$, and terminating at $j$:
  $$C(S, j) = \min_{i \in S \setminus \{j\}} \{ C(S \setminus \{j\}, i) + dist(i, j) \}$$
  Base case: $C(\{s\}, s) = 0$.
  Optimal cycle: $\min_{j \neq s} \{ C(V, j) + dist(j, s) \}$.
- **Reconstruction**: Backtracks through parent pointers to output the exact sequence of cities.

#### 3. Nearest Neighbor Heuristic (`algorithms/nearest_neighbor.py`)
- **Strategy**: Greedily chooses the closest unvisited city at each step. Uses deterministic lowest-index tie-breaking.
- **Caveat**: Can be trapped into taking extremely costly long edges on the final return leg. Route quality is sensitive to the chosen start city.

#### 4. MST-Based 2-Approximation (`algorithms/mst_approximation.py`)
- **Strategy**:
  1. Computes the Minimum Spanning Tree (MST) using Prim's algorithm on dense matrices ($\mathcal{O}(n^2)$). Note that $Cost(\text{MST}) < Cost(\text{OPT}_{\text{TSP}})$.
  2. Conceptually doubles MST edges to form an Eulerian multigraph ($Cost \le 2 \times Cost(\text{MST})$).
  3. Traverses the tree in preorder (Depth-First Search) starting at the designated start city.
  4. Shortcuts previously visited vertices. By the **Triangle Inequality** ($d(u, w) \le d(u, v) + d(v, w)$), skipping intermediate nodes never increases edge cost.
  5. Appends the start city to complete the tour.
- **Theoretical Bound**: $\text{Cost}(\text{Tour}) \le 2 \times \text{Cost}(\text{OPT})$. **Applies strictly to Metric TSP instances.**

---

## 3. Project Directory Structure

```
Traveling Salesman/
├── app.py                      # Interactive Streamlit Web Application
├── benchmark_runner.py         # Standalone CLI experimental evaluation runner
├── requirements.txt            # Python dependencies (Streamlit, Pytest, Matplotlib, etc.)
├── README.md                   # Complete documentation and SPPU viva guide
├── PROJECT_PROGRESS.md         # Milestone and verification audit log
├── algorithms/                 # Core TSP algorithm implementations
│   ├── __init__.py
│   ├── brute_force.py          # Exact O(n!) permutation solver
│   ├── held_karp.py            # Exact O(n² 2ⁿ) dynamic programming solver
│   ├── nearest_neighbor.py     # Greedy O(n²) heuristic solver
│   └── mst_approximation.py    # Metric O(n²) 2-approximation solver
├── utils/                      # Shared utilities and benchmarking
│   ├── __init__.py
│   ├── distance.py             # Euclidean generator, cost recalculator, formatter
│   ├── validation.py           # Matrix, tour, and triangle-inequality validators
│   ├── benchmarking.py         # High-resolution timing, fair execution, optimality gap
│   └── visualizations.py       # Matplotlib 2D tour mapping and performance bar charts
├── tests/                      # Automated unit and integration tests
│   ├── __init__.py
│   └── test_algorithms.py      # 28 pytest tests covering edge cases & correctness
└── outputs/                    # Output directory for exported benchmark CSVs
    └── benchmark_results.csv   # Real empirical execution metrics
```

---

## 4. Installation & Setup

### Prerequisites
- Python 3.8 or higher installed on your system.

### Step 1: Clone or Navigate to the Workspace
```bash
cd "f:\Traveling Salesman"
```

### Step 2: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 5. How to Run

### Run the Interactive Streamlit Web Application
```bash
streamlit run app.py
```
*The web interface will launch automatically at `http://localhost:8501`.*

### Run the Automated Pytest Test Suite
```bash
pytest -v tests/test_algorithms.py
```

### Run Standalone CLI Benchmarks Across City Counts ($n = 4 \dots 16$)
```bash
python benchmark_runner.py
```

---

## 6. Live Empirical Benchmark Results

The table below reflects **actual program executions** measured with `time.perf_counter()` on the host machine using Euclidean metric instances generated with seed 42:

| Cities ($n$) | Algorithm | Category | Measured Cost | Execution Time (ms) | Optimality Gap (%) | Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **4** | Held-Karp DP | Exact | 173.89 | 0.090 ms | **0.00% (Opt)** | Success |
| 4 | Brute Force | Exact | 173.89 | 0.025 ms | **0.00% (Opt)** | Success |
| 4 | Nearest Neighbor | Heuristic | 173.89 | 0.023 ms | **0.00%** | Success |
| 4 | MST 2-Approximation | Approximation | 208.43 | 0.058 ms | 19.86% | Success |
| **8** | Held-Karp DP | Exact | 227.94 | 1.869 ms | **0.00% (Opt)** | Success |
| 8 | Brute Force | Exact | 227.94 | 11.877 ms | **0.00% (Opt)** | Success |
| 8 | Nearest Neighbor | Heuristic | 227.94 | 0.034 ms | **0.00%** | Success |
| 8 | MST 2-Approximation | Approximation | 301.32 | 0.086 ms | 32.19% | Success |
| **10** | Held-Karp DP | Exact | 237.71 | **23.264 ms** | **0.00% (Opt)** | Success |
| 10 | Brute Force | Exact | 237.71 | **1045.696 ms** | **0.00% (Opt)** | Success |
| 10 | Nearest Neighbor | Heuristic | 265.20 | 0.045 ms | 11.56% | Success |
| 10 | MST 2-Approximation | Approximation | 311.31 | 0.112 ms | 30.96% | Success |
| **14** | Held-Karp DP | Exact | 256.43 | 490.411 ms | **0.00% (Opt)** | Success |
| 14 | Nearest Neighbor | Heuristic | 310.65 | 0.043 ms | 21.14% | Success |
| 14 | MST 2-Approximation | Approximation | 354.44 | 0.105 ms | 38.22% | Success |
| **16** | Held-Karp DP | Exact | 260.71 | 2268.792 ms | **0.00% (Opt)** | Success |
| 16 | Nearest Neighbor | Heuristic | 302.07 | 0.090 ms | 15.86% | Success |
| 16 | MST 2-Approximation | Approximation | 380.94 | 0.210 ms | 46.12% | Success |

### Key Experimental Takeaways:
1. **Factorial vs Exponential Crossover**: At $n = 10$, Held-Karp ($23.26\text{ ms}$) executes **45 times faster** than Brute Force ($1045.70\text{ ms}$).
2. **Exact Solution Agreement**: Brute Force and Held-Karp achieve **$100\%$ identical minimal tour costs** across all test instances.
3. **Approximation Bound Verification**: The MST 2-Approximation tour cost never exceeds $2 \times \text{OPT}$ (max observed gap was $46.12\% \ll 100\%$).
4. **Independent Cost Recalculation**: All tour distances and validity constraints are independently verified before display.

---

## 7. College Viva Q&A Guide (SPPU B.E. Computer Engineering)

#### Q1: Why is the Travelling Salesperson Problem (TSP) NP-hard?
> **Answer**: The decision version of TSP ("Does a tour of cost $\le K$ exist?") is NP-complete because the Hamiltonian Cycle problem can be reduced to it in polynomial time. Finding the minimal tour (optimization version) is at least as hard as the decision problem, placing TSP in the NP-hard class. No polynomial-time exact algorithm is known unless $\text{P} = \text{NP}$.

#### Q2: What is the difference between a Heuristic and an Approximation Algorithm?
> **Answer**:
> - A **Heuristic** (e.g., Nearest Neighbor) is an intuitive rule of thumb that performs well on average instances, but has **no theoretical guarantee** on solution quality. In the worst case, Nearest Neighbor can produce arbitrarily bad tours ($\mathcal{O}(\log n)$ ratio for metric, unbounded for general).
> - An **Approximation Algorithm** (e.g., MST 2-Approximation) mathematically guarantees that the produced solution cost is within a factor $\alpha$ of the optimal cost ($Cost \le \alpha \cdot OPT$) for all valid inputs.

#### Q3: Why does the MST 2-Approximation require the Triangle Inequality?
> **Answer**: The algorithm shortcuts the Eulerian walk of the doubled MST by skipping already visited vertices. The triangle inequality ($d(u, w) \le d(u, v) + d(v, w)$) guarantees that taking a shortcut directly between $u$ and $w$ will never cost more than traveling through the intermediate node $v$. If the triangle inequality is violated (non-metric TSP), shortcutting can increase edge costs and the $2$-approximation bound fails.

#### Q4: How is the percentage Optimality Gap defined?
> **Answer**:
> $$\text{Optimality Gap} = \frac{\text{Algorithm Cost} - \text{Optimal Cost}}{\text{Optimal Cost}} \times 100\%$$
> For exact algorithms, the gap is $0.00\%$. If no exact algorithm was executed (e.g. for large $n$), the gap is reported as `N/A` rather than fabricating an optimum.

---

## 8. Limitations & Scope Boundaries
- **Brute Force**: Excluded for $n > 10$ by default to prevent UI freezing (requires $(n-1)!$ evaluations).
- **Held-Karp**: Excluded for $n > 18$ by default to avoid exhausting RAM from storing $O(n \cdot 2^n)$ subproblem states.
- **Metric Scope**: The 2-approximation guarantee applies strictly to instances satisfying the triangle inequality (such as Euclidean straight-line coordinates). Arbitrary asymmetric or non-metric matrices are explicitly flagged in the UI.
