from Genetic import Genetic
import scheduler_utils as scheduler
import prettytable as prettytable
import tkinter as tk
from tkinter import ttk
from tkinter import Canvas, Frame, Scrollbar
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



# def print_schedule_as_table( schedule):
    
#         table = prettytable.PrettyTable(['class #','dept','Course(number,max # of students)','Room(Capacity)','Instructor(name,id)','Meeting time(id)'])
#         for cls in schedule:
#             table.add_row([
#                 str(cls.get_id()),
#                 cls.get_dept().get_name(),
#                 cls.get_course().get_name() + " (" +
#                 str(cls.get_course().get_id()) + ", " + 
#                 str(cls.get_course().get_num_of_students()) + ")",
#                 cls.get_room().get_number() + " (" + str(cls.get_room().get_seatingCapacity()) + ")",
#                 cls.get_instructor().get_name() + " (" + str(cls.get_instructor().get_id()) + ")",
#                 cls.get_meetingTime().get_time() + " (" + str(cls.get_meetingTime().get_id()) + ")"
#             ])
#         output_schedule_text.insert(tk.END, table.get_string() + "\n\n")

# root = tk.Tk()
# root.title("Timetable Scheduler")
# root.geometry("1250x800")
# root.configure(bg="#f0f2f5")

# style = ttk.Style()
# style.configure('TButton', font=('Helvetica', 12))
# style.configure('TLabel', font=('Helvetica', 12))
# style.configure('TNotebook.Tab', font=('Helvetica', 11, 'bold'))
# style.configure('TNotebook', background="#ffffff")
# style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
# style.configure("Treeview", rowheight=25, font=("Helvetica", 10))

# # Top Frame
# top_frame = ttk.Frame(root, padding=10)
# top_frame.pack(fill="x")

# notebook = ttk.Notebook(root)
# notebook.pack(expand=True, fill="both", padx=10, pady=10)

# Genetic_Generated_Schedule = ttk.Frame(notebook)
# notebook.add(Genetic_Generated_Schedule, text="Genetic Generated Schedule")

# output_schedule_text = tk.Text(Genetic_Generated_Schedule, wrap="word", font=("Consolas", 11))
# output_schedule_text.pack(expand=True, fill="both", padx=5, pady=5)








# parant1 = scheduler.generate_Schedule()
# parant2 = scheduler.generate_Schedule()

# print_schedule_as_table(parant1)
# print_schedule_as_table(parant2)


# genetic = Genetic.Genetic()
# new_chromosome = genetic.sector_based_crossover(parant1, parant2)

# print_schedule_as_table(new_chromosome)
    
# root.mainloop()



base_schedule = scheduler.generate_Schedule()
# one_point_crossover = Genetic.one_point_crossover()
# uniform_crossover = Genetic.uniform_crossover()
# sector_based_crossover = Genetic.sector_based_crossover()
Genetic = Genetic()

best_schedule_opx, opx_best_fitness, no_of_generation_opx = Genetic.genetic_algorithm(base_schedule=base_schedule, crossover_fn=Genetic.one_point_crossover)
best_schedule_uniform, uniform_best_fitness, no_of_generation_uniform = Genetic.genetic_algorithm(base_schedule=base_schedule, crossover_fn=Genetic.uniform_crossover)
best_schedule_sector, sector_best_fitness, no_of_generation_sector = Genetic.genetic_algorithm(base_schedule=base_schedule, crossover_fn=Genetic.sector_based_crossover)

# Print the best schedules and their fitness scores
print("Best Schedule (One Point Crossover):")
print("Fitness:", opx_best_fitness)
print("no of genrations:",no_of_generation_opx)

print("Best Schedule (Uniform Crossover):")
print("Fitness:", uniform_best_fitness)
print("no of genrations:",no_of_generation_uniform)

print("Best Schedule (Sector Based Crossover):")
print("Fitness:", sector_best_fitness)
print("no of genrations:",no_of_generation_sector)
