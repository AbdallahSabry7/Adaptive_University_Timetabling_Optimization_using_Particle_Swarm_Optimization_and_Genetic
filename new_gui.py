import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
from main import genetic_main, pso_main, hybrid_main
import random

class TimetableOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Timetable Optimization GUI")
        self.root.geometry("1200x800")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.ga_tab = ttk.Frame(self.notebook)
        self.pso_tab = ttk.Frame(self.notebook)
        self.hybrid_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.ga_tab, text='Genetic Algorithm')
        self.notebook.add(self.pso_tab, text='Particle Swarm')
        self.notebook.add(self.hybrid_tab, text='Hybrid GA + PSO')

        self.log_texts = {}
        self.figures = {}
        self.axes = {}
        self.canvases = {}
        self.entries = {}

        self.create_ga_tab()
        self.create_pso_tab()
        self.create_hybrid_tab()

    def create_ga_tab(self):
        self.create_controls(
            self.ga_tab, "GA",
            ["max_generations", "population_size", "Mutation_Type", "crossover_Type", "Selection_Type", "mutation_rate", "crossover_rate", "Survival_Type","initialization_type"]
        )

    def create_pso_tab(self):
        self.create_controls(
            self.pso_tab, "PSO",
            ["max_iterations", "particles_num", "w_start", "c1", "c2", "w_end", "initialization_type"]
        )

    def create_hybrid_tab(self):
        self.create_controls(
            self.hybrid_tab, "Hybrid",
            ["max_iterations", "particles_num", "Mutation_Type", "crossover_Type", "Selection_Type", "w_start", "c1", "c2", "w_end", "mutation_rate", "crossover_rate","initialization_type", "Survival_Type"]
        )

    def create_controls(self, parent, algorithm, fields):
        frame = ttk.Frame(parent)
        frame.pack(side='top', fill='x', pady=10)

        self.entries[algorithm] = {}

        options = {
            "Mutation_Type": ["WGWRGM", "random_reinitialization_M", "swap_class_assignments_M", "field_mutation"],
            "crossover_Type": ["Single Point", "Two Point", "Uniform", "sector_based", "Conflict Aware"],
            "Selection_Type": ["Ranked", "Tournament"],
            "Survival_Type": ["elitism", "generational"],
            "initialization_type": ["random", "heuristic", "weighted"]
        }
        
        default_values = {
            "max_generations": "100",
            "population_size": "50",
            "mutation_rate": "0.1",
            "crossover_rate": "0.8",
            "max_iterations": "100",
            "particles_num": "30",
            "w_start": "0.9",
            "w_end": "0.4",
            "c1": "1.5",
            "c2": "1.5",
            "Mutation_Type": "WGWRGM",
            "crossover_Type": "Single Point",
            "Selection_Type": "Ranked",
            "Survival_Type": "elitism",
            "initialization_type": "random"
        }

        for i, field in enumerate(fields):
            ttk.Label(frame, text=field).grid(row=i, column=0, sticky='e', padx=5, pady=2)
            if field in options:
                combo = ttk.Combobox(frame, values=options[field], state="readonly")
                combo.set(default_values.get(field, options[field][0]))
                combo.grid(row=i, column=1, padx=5, pady=2)
                self.entries[algorithm][field] = combo
            else:
                entry = ttk.Entry(frame)
                entry.insert(0, default_values.get(field, ""))
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.entries[algorithm][field] = entry

        ttk.Button(frame, text="Run Optimization", command=lambda: self.run_optimization(algorithm)).grid(row=len(fields), column=0, columnspan=2, pady=10)

        log_text = tk.Text(parent, height=10)
        log_text.pack(fill='x', padx=10, pady=10)
        self.log_texts[algorithm] = log_text

        fig, ax = plt.subplots(figsize=(5, 3))
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack(fill='both', expand=True)

        self.figures[algorithm] = fig
        self.axes[algorithm] = ax
        self.canvases[algorithm] = canvas
        
        schedule_label = ttk.Label(parent, text="Best Schedule:")
        schedule_label.pack(padx=10, anchor="w")
        schedule_text = tk.Text(parent, height=10)
        schedule_text.pack(fill='both', padx=10, pady=5)
        self.schedule_display = self.schedule_display if hasattr(self, 'schedule_display') else {}
        self.schedule_display[algorithm] = schedule_text

    def run_optimization(self, algorithm):
        self.log(algorithm, f"Starting {algorithm} optimization...")
        params = {key: self.entries[algorithm][key].get() for key in self.entries[algorithm]}
        thread = threading.Thread(target=self.call_algorithm, args=(algorithm, params))
        thread.start()

    def call_algorithm(self, algorithm, params):
        import time
        SEED = 42
        random.seed(SEED)
        if algorithm == "GA":
            result = genetic_main(
            int(params["max_generations"]), int(params["population_size"]),
            params["Mutation_Type"], params["crossover_Type"], params["Selection_Type"],
            float(params["mutation_rate"]), float(params["crossover_rate"]), params["initialization_type"],
            params["Survival_Type"]
        )

        elif algorithm == "PSO":
            result = pso_main(
                int(params["max_iterations"]), int(params["particles_num"]),
                float(params["w_start"]), float(params["c1"]), float(params["c2"]), float(params["w_end"])
            )
        elif algorithm == "Hybrid":
            result = hybrid_main(
                int(params["max_iterations"]), int(params["particles_num"]),
                params["Mutation_Type"], params["crossover_Type"], params["Selection_Type"],
                float(params["w_start"]), float(params["c1"]), float(params["c2"]), float(params["w_end"]),
                float(params["mutation_rate"]), float(params["crossover_rate"]), params["initialization_type"]
            )
        schedule, best_fitness, fitness_over_time = result
        schedule, best_fitness, fitness_over_time = result
        self.plot_fitness(algorithm, fitness_over_time)
        self.log(algorithm, f"{algorithm} optimization completed. Best Fitness: {best_fitness:.4f}")
        self.display_schedule(algorithm, schedule)


    def plot_fitness(self, algorithm, fitness):
        ax = self.axes[algorithm]
        canvas = self.canvases[algorithm]
        ax.clear()
        ax.plot(range(1, len(fitness)+1), fitness, marker='o')
        ax.set_title(f"{algorithm} Fitness Over Generations")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Fitness")
        canvas.draw()

    def log(self, algorithm, message):
        text_widget = self.log_texts.get(algorithm)
        if text_widget:
            text_widget.insert(tk.END, message + '\n')
            text_widget.see(tk.END)
            
    def display_schedule(self, algorithm, schedule):
        text_widget = self.schedule_display.get(algorithm)
        if not text_widget:
            return

        text_widget.delete("1.0", tk.END)
        for item in schedule:
            line = f"Course: {item.get('course', '')}, Instructor: {item.get('instructor', '')}, " \
                f"Room: {item.get('room', '')}, Day: {item.get('day', '')}, Time: {item.get('time', '')}\n"
            text_widget.insert(tk.END, line)


if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableOptimizerGUI(root)
    root.mainloop()
