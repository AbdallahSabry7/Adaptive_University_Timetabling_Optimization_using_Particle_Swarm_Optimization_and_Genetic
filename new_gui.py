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

        self.entries = {}
        self.schedule_display = {}
        self.log_texts = {}
        self.figures = {}
        self.axes = {}
        self.canvases = {}
        self.subtabs = {}

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
        main_frame = ttk.Frame(parent)
        main_frame.pack(side='top', fill='both', expand=True)

        # --- Top: Control Inputs ---
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(side='top', fill='x', pady=10)
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
            "c1": "2.0",
            "c2": "2.0"
        }


        for i, field in enumerate(fields):
            ttk.Label(controls_frame, text=field).grid(row=i, column=0, sticky='e', padx=5, pady=2)
            if field in options:
                combo = ttk.Combobox(controls_frame, values=options[field], state="readonly")
                combo.current(0)
                combo.grid(row=i, column=1, padx=5, pady=2)
                self.entries[algorithm][field] = combo
            else:
                entry = ttk.Entry(controls_frame)
                entry.insert(0, default_values.get(field, ""))  # Insert default if available
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.entries[algorithm][field] = entry


        ttk.Button(controls_frame, text="Run Optimization", command=lambda: self.run_optimization(algorithm)).grid(
            row=len(fields), column=0, columnspan=2, pady=10
        )

        # --- Bottom: Subtabs ---
        subtabs = ttk.Notebook(main_frame)
        subtabs.pack(fill='both', expand=True)
        self.subtabs[algorithm] = subtabs

        # Schedule Tab
        schedule_tab = ttk.Frame(subtabs)
        subtabs.add(schedule_tab, text='Schedule')
        schedule_text = tk.Text(schedule_tab)
        schedule_text.pack(fill='both', expand=True)
        self.schedule_display[algorithm] = schedule_text

        # Plot Tab
        plot_tab = ttk.Frame(subtabs)
        subtabs.add(plot_tab, text='Fitness Plot')
        fig, ax = plt.subplots(figsize=(5, 3))
        canvas = FigureCanvasTkAgg(fig, master=plot_tab)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self.figures[algorithm] = fig
        self.axes[algorithm] = ax
        self.canvases[algorithm] = canvas

        # Log Tab
        log_tab = ttk.Frame(subtabs)
        subtabs.add(log_tab, text='Log')
        log_text = tk.Text(log_tab, height=10)
        log_text.pack(fill='both', expand=True)
        self.log_texts[algorithm] = log_text

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
            
    def sort_column(self, tree, col):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        # Detect if sorting numerically or lexically
        try:
            data.sort(key=lambda t: float(t[0]))
        except ValueError:
            data.sort(key=lambda t: t[0])

        reverse = self._sort_state.get(col, False)
        data.reverse() if reverse else None
        self._sort_state[col] = not reverse

        for index, (_, child) in enumerate(data):
            tree.move(child, '', index)

        # Update column headers to show sort direction
        for c in tree["columns"]:
            direction = "▲" if not self._sort_state.get(c, False) else "▼"
            tree.heading(c, text=f"{c} {direction if c == col else '▲▼'}",
                        command=lambda _col=c: self.sort_column(tree, _col))


            
    def display_schedule(self, algorithm, schedule):
        if algorithm in self.schedule_display:
            old_widget = self.schedule_display[algorithm]
            old_widget.destroy()

        parent_tab = self.subtabs[algorithm].nametowidget(self.subtabs[algorithm].tabs()[0])
        tree = ttk.Treeview(parent_tab, columns=("Dept", "Course", "Instructor", "Room", "Time"),
                    show="headings", style="Custom.Treeview")

        tree.pack(fill='both', expand=True, padx=2, pady=2)
        self.schedule_display[algorithm] = tree

        self._sort_state = {}  # Track sort direction for each column

        style = ttk.Style()
        style.theme_use("default")

        # --- Treeview style with visible column borders ---
        style.configure("Custom.Treeview",
            background="white",
            foreground="black",
            rowheight=25,
            fieldbackground="white",
            bordercolor="black",
            borderwidth=1,
            relief="solid"
        )

        style.map('Custom.Treeview', background=[('selected', '#ececec')])

        # --- Header style ---
        style.configure("Custom.Treeview.Heading",
            font=("Helvetica", 10, "bold"),
            background="#cfd8dc",  # Light grey-blue
            foreground="black",
            borderwidth=1,
            relief="raised"
        )

        style.layout("Custom.Treeview", [
            ("Treeview.treearea", {'sticky': 'nswe'})
        ])


        columns = ("Dept", "Course", "Instructor", "Room", "Time")
        for col in columns:
            tree.heading(col, text=col + " ▲▼", command=lambda _col=col: self.sort_column(tree, _col))
            tree.column(col, anchor='center', stretch=True, width=150)

        try:
            sorted_schedule = sorted(schedule, key=lambda cls: (
                cls.get_dept().get_name(),
                cls.get_meetingTime().get_id()
            ))
        except Exception as e:
            self.log(algorithm, f"Error sorting schedule: {e}")
            sorted_schedule = schedule

        for cls in sorted_schedule:
            try:
                tree.insert("", "end", values=(
                    cls.get_dept().get_name(),
                    cls.get_course().get_name(),
                    cls.get_instructor().get_name(),
                    cls.get_room().get_number(),
                    cls.get_meetingTime().get_time()
                ))
            except Exception as e:
                self.log(algorithm, f"[Error displaying class: {e}]")





if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableOptimizerGUI(root)
    root.mainloop()
