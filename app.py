from __future__ import annotations
import io
import math
import pandas as pd
import streamlit as st
from typing import List, Tuple, Optional, Dict, Any

from utils.distance import (
    generate_euclidean_cities,
    calculate_tour_cost,
    format_route,
    city_names_for_count,
)
from utils.validation import (
    validate_distance_matrix,
    validate_tour,
    check_metric_property,
)
from utils.benchmarking import (
    ALGORITHM_REGISTRY,
    LIMIT_BRUTE_FORCE,
    LIMIT_HELD_KARP,
    run_benchmark_suite,
)
from utils.visualizations import (
    plot_tsp_route,
    plot_execution_times_chart,
    plot_distance_and_gap_chart,
)
from algorithms.mst_approximation import compute_mst_prim


# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Travelling Salesperson Problem Optimization Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Clean Corporate / Research Styling
# -----------------------------------------------------------------------------
# Application Header (Theme-Adaptive for Light and Dark Modes)
# -----------------------------------------------------------------------------
st.title("Travelling Salesperson Problem Optimization Platform")
st.markdown(
    "Comparative evaluation of Exact, Heuristic, and Approximation algorithms on complete network topologies."
)


# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
st.sidebar.markdown("### Configuration")

input_mode = st.sidebar.radio(
    "Data Source",
    ["2D Euclidean Generation", "Manual Distance Matrix"],
    index=0,
    help="Euclidean coordinates guarantee metric symmetry and triangle inequality."
)

coordinates: Optional[List[Tuple[float, float]]] = None
city_names: List[str] = []
distance_matrix: List[List[float]] = []

if input_mode == "2D Euclidean Generation":
    num_cities = st.sidebar.slider(
        "Number of Nodes (n)",
        min_value=3,
        max_value=20,
        value=6,
        help="Sizes up to 10 support Brute Force; up to 18 support Held-Karp."
    )
    seed = st.sidebar.number_input("Random Seed", min_value=0, max_value=999999, value=42)

    city_names, coordinates, distance_matrix = generate_euclidean_cities(n=num_cities, seed=seed)
    st.sidebar.caption(f"Generated {num_cities} reproducible Euclidean node coordinates.")

else:
    st.sidebar.markdown("#### Distance Matrix Input")
    st.sidebar.caption("Enter square symmetric matrix rows separated by newlines.")
    
    sample_default = "0, 10, 15, 20\n10, 0, 35, 25\n15, 35, 0, 30\n20, 25, 30, 0"
    matrix_raw = st.sidebar.text_area("Distance Matrix Values", value=sample_default, height=140)

    parsed_matrix = []
    lines = [line.strip() for line in matrix_raw.strip().split("\n") if line.strip()]
    for line in lines:
        parts = [p.strip() for p in line.replace(",", " ").split() if p.strip()]
        parsed_matrix.append(parts)

    valid_mat, mat_err, validated = validate_distance_matrix(parsed_matrix)
    if not valid_mat:
        st.sidebar.error(f"Matrix Validation Error: {mat_err}")
        st.stop()
    else:
        distance_matrix = validated
        num_cities = len(distance_matrix)
        city_names = city_names_for_count(num_cities)
        st.sidebar.success(f"Valid {num_cities}x{num_cities} symmetric matrix loaded.")

start_city_label = st.sidebar.selectbox(
    "Designated Origin Node",
    options=[f"{city_names[i]} (Index {i})" for i in range(num_cities)],
    index=0
)
start_city = int(start_city_label.split("Index ")[1].replace(")", ""))

st.sidebar.markdown("---")
st.sidebar.markdown("### Solvers")

col_sel1, col_sel2 = st.sidebar.columns(2)
run_bf = col_sel1.checkbox("Brute Force", value=(num_cities <= LIMIT_BRUTE_FORCE))
run_hk = col_sel2.checkbox("Held-Karp DP", value=(num_cities <= LIMIT_HELD_KARP))
run_nn = col_sel1.checkbox("Nearest Neighbor", value=True)
run_mst = col_sel2.checkbox("MST 2-Approx", value=True)

allow_override = st.sidebar.checkbox(
    "Override exact size limit",
    value=False,
    help="Force exact solver execution on instances exceeding default limits. May incur significant execution latency."
)

# -----------------------------------------------------------------------------
# Metric Property Verification Banner
# -----------------------------------------------------------------------------
is_metric, metric_msg, violating_triplet = check_metric_property(distance_matrix)

col_top1, col_top2 = st.columns([2, 1])
with col_top1:
    if is_metric:
        st.success(
            "**Metric Property Confirmed:** Triangle inequality is satisfied across all triplets. "
            "The MST 2-Approximation theoretical bound (Cost ≤ 2 × OPT) holds."
        )
    else:
        st.warning(
            f"**Non-Metric Input:** {metric_msg} "
            "Note: The MST 2-Approximation will execute, but theoretical 2x optimality guarantees require the triangle inequality."
        )

with col_top2:
    st.info(f"Active Instance: {num_cities} Nodes | Origin Node: {city_names[start_city]}")

# -----------------------------------------------------------------------------
# Solver Execution
# -----------------------------------------------------------------------------
selected_keys = []
if run_bf:
    selected_keys.append("brute_force")
if run_hk:
    selected_keys.append("held_karp")
if run_nn:
    selected_keys.append("nearest_neighbor")
if run_mst:
    selected_keys.append("mst_approximation")

if not selected_keys:
    st.warning("Select at least one algorithm solver in the sidebar.")
    st.stop()

if "brute_force" in selected_keys and num_cities > LIMIT_BRUTE_FORCE and not allow_override:
    st.warning(f"Brute Force solver skipped: Node count n={num_cities} exceeds default limit of {LIMIT_BRUTE_FORCE}. Check 'Override exact size limit' to run.")

if "held_karp" in selected_keys and num_cities > LIMIT_HELD_KARP and not allow_override:
    st.warning(f"Held-Karp solver skipped: Node count n={num_cities} exceeds default limit of {LIMIT_HELD_KARP}. Check 'Override exact size limit' to run.")

benchmark_data = run_benchmark_suite(
    distance_matrix=distance_matrix,
    start_city=start_city,
    selected_algos=selected_keys,
    city_names=city_names,
    allow_large_exact=allow_override,
)

results = benchmark_data["results"]
optimal_cost = benchmark_data["optimal_cost"]

# -----------------------------------------------------------------------------
# Results Presentation
# -----------------------------------------------------------------------------
st.markdown("### Benchmark Results & Performance Summary")

table_rows = []
for r in results:
    table_rows.append({
        "Algorithm": r.display_name,
        "Paradigm": r.category,
        "Complexity": r.time_complexity,
        "Theoretical Bound": r.guarantee,
        "Tour Cost": f"{r.cost:.2f}" if r.status == "Success" else "N/A",
        "Optimality Gap": f"{r.optimality_gap_pct:.2f}%" if r.optimality_gap_pct is not None else ("0.00% (Opt)" if r.cost == optimal_cost and r.status == "Success" else "N/A"),
        "Execution Time": f"{r.execution_time_sec * 1000.0:.3f} ms" if r.status == "Success" else "0.000 ms",
        "Status": r.status,
        "Route Sequence": r.formatted_route,
    })

df_results = pd.DataFrame(table_rows)
st.dataframe(df_results, use_container_width=True, hide_index=True)

successful_results = [r for r in results if r.status == "Success"]
if successful_results:
    best_res = min(successful_results, key=lambda x: x.cost)
    fastest_res = min(successful_results, key=lambda x: x.execution_time_sec)
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Reference Optimum", f"{optimal_cost:.2f}" if optimal_cost is not None else "N/A (No exact solver)")
    with col_m2:
        st.metric("Lowest Cost Tour", f"{best_res.cost:.2f}", delta=best_res.display_name)
    with col_m3:
        st.metric("Fastest Solver", f"{fastest_res.execution_time_sec*1000:.3f} ms", delta=fastest_res.display_name)
    with col_m4:
        st.metric("Valid Tours Verified", f"{len(successful_results)}/{len(results)}", delta="Complete")

csv_buffer = io.StringIO()
df_results.to_csv(csv_buffer, index=False)
st.download_button(
    label="Export Results (CSV)",
    data=csv_buffer.getvalue(),
    file_name=f"tsp_benchmark_n{num_cities}.csv",
    mime="text/csv"
)

# -----------------------------------------------------------------------------
# Detailed Views Tabs
# -----------------------------------------------------------------------------
st.markdown("---")
tab_routes, tab_perf, tab_edu, tab_faq = st.tabs([
    "Route Visualizer",
    "Performance Analytics",
    "Algorithm Reference",
    "Frequently Asked Questions"
])

# Tab 1: Route Visualizer
with tab_routes:
    if coordinates is not None:
        st.subheader("2D Tour Visualization")
        success_names = [r.display_name for r in successful_results]
        
        if success_names:
            selected_view = st.selectbox("Inspect Route Graph", success_names)
            chosen_res = next(r for r in successful_results if r.display_name == selected_view)
            
            mst_tree_edges = None
            if chosen_res.key == "mst_approximation":
                mst_tree_edges = compute_mst_prim(distance_matrix, start_city)
                st.caption("Note: Dashed lines represent the underlying Minimum Spanning Tree from which the tour was derived.")

            color_map = {
                "Brute Force": "#2563EB",
                "Held-Karp DP": "#7C3AED",
                "Nearest Neighbor": "#059669",
                "MST 2-Approximation": "#D97706"
            }
            tour_color = color_map.get(chosen_res.display_name, "#2563EB")

            fig_tour = plot_tsp_route(
                coordinates=coordinates,
                tour=chosen_res.route,
                city_names=city_names,
                algo_name=f"{chosen_res.display_name} Tour",
                total_cost=chosen_res.cost,
                color=tour_color,
                mst_edges=mst_tree_edges
            )
            st.pyplot(fig_tour)
            st.code(f"Route: {chosen_res.formatted_route}", language="text")
        else:
            st.info("No successful route available for visualization.")
    else:
        st.info("Coordinate plotting is unavailable for custom matrices without coordinate definitions. Route sequences are provided in the table above.")

# Tab 2: Performance Analytics
with tab_perf:
    st.subheader("Performance & Quality Comparison")
    dict_results = [r.to_dict() for r in results]
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fig_time = plot_execution_times_chart(dict_results)
        st.pyplot(fig_time)
        st.caption("Execution times measured using high-resolution performance counters.")

    with col_c2:
        fig_dist = plot_distance_and_gap_chart(dict_results)
        st.pyplot(fig_dist)
        st.caption("Tour distances independently recalculated by summing edge weights.")

# Tab 3: Algorithm Reference
with tab_edu:
    st.subheader("Methodology & Complexity Analysis")

    exp_bf = st.expander("Brute Force Permutation Search", expanded=False)
    with exp_bf:
        st.markdown("""
        **Paradigm**: Exhaustive Search (Exact).  
        **Method**: Fixes the starting origin to break rotational symmetry, enumerates all (n-1)! permutations of remaining nodes, calculates each complete tour's cost, and retains the minimum.  
        **Time Complexity**: O((n-1)! * n) = O(n!).  
        **Space Complexity**: O(n).  
        **Optimality**: Guaranteed global optimum.  
        **Characteristics**: Strictly limited to small instances (n <= 10) due to factorial scaling.
        """)

    exp_hk = st.expander("Held-Karp Dynamic Programming", expanded=False)
    with exp_hk:
        st.markdown("""
        **Paradigm**: Dynamic Programming with Bitmasking (Exact).  
        **Recurrence Relation**:  
        Let C(S, j) denote the minimum cost path starting at origin s, visiting all nodes in subset S, and terminating at node j:  
        `C(S, j) = min_{i in S, i != j} { C(S \\ {j}, i) + dist(i, j) }`  
        Base condition: C({s}, s) = 0.  
        Optimal cycle: `min_{j != s} { C(V, j) + dist(j, s) }`.  
        **Time Complexity**: O(n^2 * 2^n).  
        **Space Complexity**: O(n * 2^n) states stored in memory.  
        **Optimality**: Guaranteed global optimum.  
        **Characteristics**: Eliminates redundant permutation evaluations; practical up to n = 18-20 on modern hardware.
        """)

    exp_nn = st.expander("Nearest Neighbor Heuristic", expanded=False)
    with exp_nn:
        st.markdown("""
        **Paradigm**: Greedy Heuristic.  
        **Method**: Starting at the designated origin, greedily selects the closest unvisited node at each step. Returns to the origin once all nodes are visited.  
        **Time Complexity**: O(n^2) when scanning an n x n distance matrix.  
        **Space Complexity**: O(n).  
        **Optimality**: No theoretical guarantee.  
        **Characteristics**: Highly efficient, but greedy choices can force an expensive final return edge.
        """)

    exp_mst = st.expander("MST 2-Approximation (Metric TSP)", expanded=False)
    with exp_mst:
        st.markdown("""
        **Paradigm**: Approximation Algorithm.  
        **Method**:  
        1. Computes the Minimum Spanning Tree (MST) using Prim's algorithm (Cost(MST) < Cost(OPT)).  
        2. Conceptually doubles MST edges to form an Eulerian multigraph (Cost <= 2 * Cost(MST)).  
        3. Traverses the tree in preorder (Depth-First Search).  
        4. Shortcuts previously visited nodes. Due to the triangle inequality, shortcut edges never increase cost.  
        5. Returns to origin to complete the cycle.  
        **Time Complexity**: O(n^2) for dense graphs.  
        **Space Complexity**: O(n).  
        **Approximation Ratio**: Cost <= 2 * OPT (Strictly requires triangle inequality).
        """)

    st.markdown("### Complexity Scaling Comparison")
    growth_data = [
        {"n": "4", "n!": "24", "n² 2ⁿ": "256", "n²": "16"},
        {"n": "8", "n!": "40,320", "n² 2ⁿ": "16,384", "n²": "64"},
        {"n": "10", "n!": "3,628,800", "n² 2ⁿ": "102,400", "n²": "100"},
        {"n": "12", "n!": "479,001,600", "n² 2ⁿ": "589,824", "n²": "144"},
        {"n": "16", "n!": "2.09 × 10¹³", "n² 2ⁿ": "1.67 × 10⁷", "n²": "256"},
        {"n": "20", "n!": "2.43 × 10¹⁸", "n² 2ⁿ": "4.19 × 10⁸", "n²": "400"},
    ]
    st.table(pd.DataFrame(growth_data))

# Tab 4: Theoretical FAQ
with tab_faq:
    st.subheader("Frequently Asked Questions & Theoretical Concepts")

    st.markdown("""
    **Computational Complexity and NP-Hard Classification**  
    The decision version of the Travelling Salesperson Problem is NP-complete, as the Hamiltonian Cycle problem reduces to it in polynomial time. The optimization problem of finding the minimum cost tour is NP-hard. No polynomial-time exact algorithm is known unless P = NP.

    **Heuristic vs. Approximation Guarantees**  
    A heuristic (such as Nearest Neighbor) is an intuitive strategy that yields practical solutions rapidly, but offers no theoretical upper bound on how far the output may deviate from the optimal tour. An approximation algorithm (such as the MST 2-Approximation) mathematically guarantees that the produced tour cost does not exceed a constant multiple of the optimum (Cost <= 2 * OPT) under specified assumptions.

    **Role of the Triangle Inequality in Metric Approximations**  
    The MST 2-approximation relies on shortcutting intermediate visited vertices. The triangle inequality (dist(u, w) <= dist(u, v) + dist(v, w)) guarantees that skipping intermediate vertices will not increase total edge cost. If the triangle inequality is violated, shortcutting can increase path costs and the 2x bound fails.

    **Held-Karp Dynamic Programming State Space Reduction**  
    Held-Karp utilizes the Principle of Optimality. Each subproblem is defined by the pair (S, j), where S is the subset of visited vertices and j is the current endpoint. Rather than re-evaluating all (n-1)! permutations of S, Held-Karp retains only the minimum-cost path for each (S, j), reducing time complexity from O(n!) to O(n^2 * 2^n).

    **Optimality Gap Formulation**  
    Optimality Gap (%) = ((Algorithm Cost - Optimal Cost) / Optimal Cost) * 100.  
    Exact algorithms produce an optimality gap of 0.00%. When no exact solver is executed, the gap is reported as N/A rather than using an unverified estimate.
    """)
