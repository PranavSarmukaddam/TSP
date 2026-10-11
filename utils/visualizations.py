from __future__ import annotations
import math
from typing import List, Tuple, Optional, Dict, Any
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def plot_tsp_route(
    coordinates: List[Tuple[float, float]],
    tour: List[int],
    city_names: List[str],
    algo_name: str = "TSP Tour",
    total_cost: Optional[float] = None,
    color: str = "#2563EB",
    mst_edges: Optional[List[Tuple[int, int, float]]] = None
) -> plt.Figure:
    """
    Generate a 2D Matplotlib plot of cities and the TSP tour route.
    Highlights the starting city, city labels, and edge directions.
    """
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#F8FAFC")

    # If MST edges are provided (for MST 2-approx visualization), draw them faintly in the background
    if mst_edges:
        for u, v, _ in mst_edges:
            x_vals = [coordinates[u][0], coordinates[v][0]]
            y_vals = [coordinates[u][1], coordinates[v][1]]
            ax.plot(x_vals, y_vals, color="#94A3B8", linestyle="--", linewidth=1.2, alpha=0.6, zorder=1)

    # Plot tour edges
    if tour and len(tour) > 1:
        xs = [coordinates[idx][0] for idx in tour]
        ys = [coordinates[idx][1] for idx in tour]
        ax.plot(xs, ys, color=color, linewidth=2.2, linestyle="-", alpha=0.85, zorder=2, label="Tour Path")

        # Add subtle directional arrows along tour edges
        for i in range(len(tour) - 1):
            u, v = tour[i], tour[i + 1]
            x1, y1 = coordinates[u]
            x2, y2 = coordinates[v]
            dx, dy = x2 - x1, y2 - y1
            dist = math.hypot(dx, dy)
            if dist > 1e-3:
                # Place arrow around midpoint
                mid_x = x1 + dx * 0.55
                mid_y = y1 + dy * 0.55
                ax.annotate(
                    "",
                    xy=(mid_x + dx * 0.05, mid_y + dy * 0.05),
                    xytext=(mid_x, mid_y),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5),
                    zorder=3
                )

    # Plot city nodes
    x_all = [c[0] for c in coordinates]
    y_all = [c[1] for c in coordinates]
    ax.scatter(x_all, y_all, color="#3B82F6", s=140, edgecolors="#1E3A8A", linewidths=1.5, zorder=4, label="Cities")

    # Highlight start city
    if tour and len(tour) > 0:
        start_idx = tour[0]
        ax.scatter(
            [coordinates[start_idx][0]],
            [coordinates[start_idx][1]],
            color="#EF4444",
            s=220,
            edgecolors="#991B1B",
            linewidths=2.0,
            zorder=5,
            label=f"Start City ({city_names[start_idx]})"
        )

    # Label each city
    for i, (x, y) in enumerate(coordinates):
        name = city_names[i] if i < len(city_names) else f"{i}"
        ax.text(
            x, y + 1.8,
            name,
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="bottom",
            color="#0F172A",
            zorder=6,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFFFFF", edgecolor="#CBD5E1", alpha=0.85)
        )

    title_str = f"{algo_name}"
    if total_cost is not None:
        title_str += f" | Total Distance: {total_cost:.2f}"
    ax.set_title(title_str, fontsize=12, fontweight="bold", pad=12, color="#0F172A")
    ax.set_xlabel("X Coordinate", fontsize=10, color="#334155")
    ax.set_ylabel("Y Coordinate", fontsize=10, color="#334155")
    ax.grid(True, linestyle=":", alpha=0.5, color="#CBD5E1")
    ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
    fig.tight_layout()

    return fig


def plot_execution_times_chart(results: List[Dict[str, Any]]) -> plt.Figure:
    """
    Horizontal bar chart comparing execution times across algorithms.
    Converts times to milliseconds for readability.
    """
    valid_res = [r for r in results if r["status"] == "Success"]
    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#F8FAFC")

    if not valid_res:
        ax.text(0.5, 0.5, "No successful executions to display", ha="center", va="center")
        return fig

    names = [r["display_name"] for r in valid_res]
    times_ms = [max(r["execution_time_sec"] * 1000.0, 0.0001) for r in valid_res]
    colors = ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B"][:len(names)]

    y_pos = range(len(names))
    bars = ax.barh(y_pos, times_ms, color=colors, edgecolor="#334155", height=0.55, alpha=0.9)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10, fontweight="bold", color="#1E293B")
    ax.set_xlabel("Execution Time (milliseconds)", fontsize=10, color="#334155")
    ax.set_title("Algorithm Execution Time Comparison (Lower is Faster)", fontsize=12, fontweight="bold", pad=10)
    ax.grid(axis="x", linestyle=":", alpha=0.6, color="#CBD5E1")

    # Add numeric labels to bars
    for bar, t_ms in zip(bars, times_ms):
        width = bar.get_width()
        text_label = f"{t_ms:.3f} ms" if t_ms < 1000 else f"{t_ms/1000:.2f} s"
        ax.text(
            width * 1.03 + 0.01,
            bar.get_y() + bar.get_height() / 2,
            text_label,
            va="center",
            ha="left",
            fontsize=9,
            fontweight="bold",
            color="#0F172A"
        )

    # Set x-limit with some padding
    max_val = max(times_ms)
    ax.set_xlim(0, max_val * 1.25 + 0.05)
    fig.tight_layout()
    return fig


def plot_distance_and_gap_chart(results: List[Dict[str, Any]]) -> plt.Figure:
    """
    Bar chart comparing tour distances and optimality gaps across algorithms.
    """
    valid_res = [r for r in results if r["status"] == "Success"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), dpi=100)
    fig.patch.set_facecolor("#FFFFFF")
    ax1.set_facecolor("#F8FAFC")
    ax2.set_facecolor("#F8FAFC")

    if not valid_res:
        ax1.text(0.5, 0.5, "No data", ha="center", va="center")
        ax2.text(0.5, 0.5, "No data", ha="center", va="center")
        return fig

    names = [r["display_name"] for r in valid_res]
    costs = [r["cost"] for r in valid_res]
    colors = ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B"][:len(names)]

    # Chart 1: Tour Distance
    x_pos = range(len(names))
    bars1 = ax1.bar(x_pos, costs, color=colors, edgecolor="#334155", width=0.55, alpha=0.9)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(names, rotation=20, ha="right", fontsize=9, fontweight="bold")
    ax1.set_ylabel("Total Tour Distance", fontsize=10, color="#334155")
    ax1.set_title("Tour Distance (Lower is Better)", fontsize=11, fontweight="bold", pad=8)
    ax1.grid(axis="y", linestyle=":", alpha=0.6, color="#CBD5E1")

    for bar, c in zip(bars1, costs):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.01,
            f"{c:.1f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold"
        )

    # Chart 2: Optimality Gap (%)
    has_gaps = any(r.get("optimality_gap_pct") is not None for r in valid_res)
    if has_gaps:
        gaps = [r.get("optimality_gap_pct") if r.get("optimality_gap_pct") is not None else 0.0 for r in valid_res]
        bars2 = ax2.bar(x_pos, gaps, color="#EF4444", edgecolor="#991B1B", width=0.55, alpha=0.85)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(names, rotation=20, ha="right", fontsize=9, fontweight="bold")
        ax2.set_ylabel("Optimality Gap (%)", fontsize=10, color="#334155")
        ax2.set_title("Optimality Gap vs Optimal (0% = Optimal)", fontsize=11, fontweight="bold", pad=8)
        ax2.grid(axis="y", linestyle=":", alpha=0.6, color="#CBD5E1")

        for bar, g in zip(bars2, gaps):
            label = f"{g:.1f}%" if g > 0 else "0.0% (Opt)"
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3,
                label,
                ha="center",
                va="bottom",
                fontsize=8.5,
                fontweight="bold"
            )
        max_gap = max(gaps) if gaps else 0
        ax2.set_ylim(0, max(max_gap * 1.25, 5.0))
    else:
        ax2.text(0.5, 0.5, "Optimal cost not available\n(Run Exact algorithm to view gap)",
                 ha="center", va="center", fontsize=9, color="#64748B")
        ax2.set_title("Optimality Gap (%)", fontsize=11, fontweight="bold")

    fig.tight_layout()
    return fig
