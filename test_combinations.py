import matplotlib.pyplot as plt
import numpy as np
from main import hybrid_main
import matplotlib

def test_parameter_combinations(log_callback=print):
    mutation_types = ["WGWRGM", "random_reinitialization_M", "swap_class_assignments_M", "field_mutation"]
    crossover_types = ["Single Point", "Two Point", "Uniform", "sector_based", "Conflict Aware"]
    selection_types = ["Ranked", "Tournament"]
    initialization_types = ["random", "heuristic", "weighted"]

    all_combos = [
        (cross, mutation, selection, init)
        for cross in crossover_types
        for mutation in mutation_types
        for selection in selection_types
        for init in initialization_types
    ]

    results = {}

    log_callback("Starting parameter test...")
    for i, (cross, mutation, selection, init) in enumerate(all_combos):
        log_callback(f"[{i+1}/{len(all_combos)}] Testing combo: {cross}, {mutation}, {selection}, {init}")
        fitness_scores = []

        for run in range(30):  
            try:
                result = hybrid_main(
                    200, 30, mutation, cross, selection,
                    0.9, 1, 2, 0.4, 0.2, 0.9, init,
                    log_callback=None  
                )
                _, best_fitness, _ = result
                fitness_scores.append(best_fitness)
            except Exception as e:
                log_callback(f"Error during run {run+1}: {e}")
                continue

        average_fitness = np.mean(fitness_scores)
        key = f"{cross}_{mutation}_{selection}_{init}"
        results[key] = average_fitness

    plot_fig = plot_results(results, log_callback)  
    return results, plot_fig


matplotlib.use('Agg') 

def plot_results(results, log_callback=print):
    top_n = 20
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)[:top_n]
    combinations, averages = zip(*sorted_results)

    fig, ax = plt.subplots(figsize=(12, 8), dpi=120)
    ax.bar(range(len(combinations)), averages, color='skyblue')
    ax.set_xticks(range(len(combinations)))
    ax.set_xticklabels(combinations, rotation=45, ha='right')
    ax.set_ylabel('Average Fitness over 30 Runs')
    ax.set_title('Top 20 GA Parameter Combination Performance')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for i, v in enumerate(averages):
        ax.text(i, v + 0.01, f"{v:.3f}", ha='center')

    plt.tight_layout()
    fig.savefig('parameter_combinations_performance_top20.png')
    log_callback("✅ Saved top 20 performance plot as parameter_combinations_performance_top20.png")

    return fig



