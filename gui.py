import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
    QSpinBox, QTableWidget, QTableWidgetItem, QDoubleSpinBox,
    QMessageBox, QComboBox, QFormLayout, QGroupBox, QScrollArea, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from main import pso_main
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotWindow(QWidget):
    def __init__(self, global_fitness_overtime, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PSO Fitness Convergence")
        self.setGeometry(150, 150, 600, 400)

        layout = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.canvas)

        self.ax = self.canvas.figure.subplots()
        
        iterations = list(range(1, len(global_fitness_overtime) + 1))
        self.ax.plot(iterations, global_fitness_overtime, label="Fitness over Iterations", color='blue')
        
        self.ax.set_title("Convergence Plot")
        self.ax.set_xlabel("Iteration")
        self.ax.set_ylabel("Fitness")
        self.ax.legend()

        self.setLayout(layout)



class PSOThread(QThread):
    finished = pyqtSignal(object, float, list)
    error = pyqtSignal(str)

    def __init__(self, iterations, population_size, mutation_type, cross_type, Selection_Type,
                w_start, c1, c2, w_end, mutation_rate, crossover_rate):
        super().__init__()
        self.iterations = iterations
        self.population_size = population_size
        self.mutation_type = mutation_type
        self.cross_type = cross_type
        self.Selection_Type = Selection_Type
        self.w_start = w_start
        self.c1 = c1
        self.c2 = c2
        self.w_end = w_end
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

    def run(self):
        try:
            best_schedule, best_fitness,global_fitness_overtime = pso_main(
                self.iterations, self.population_size, self.mutation_type, self.cross_type,
                self.Selection_Type, self.w_start, self.c1, self.c2,
                self.w_end, self.mutation_rate, self.crossover_rate
            )
            self.finished.emit(best_schedule, best_fitness,global_fitness_overtime)
        except Exception as e:
            self.error.emit(str(e))


class TimetableOptimizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Timetable Optimizer - PSO")
        self.setGeometry(100, 100, 800, 600)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        outer_container = QWidget()
        scroll.setWidget(outer_container)

        main_layout = QVBoxLayout(outer_container)

        general_form = QFormLayout()
        self.iter_input = self._add_spinbox("Number of Iterations", 10, 1000, 100)
        self.pop_input = self._add_spinbox("Swarm Size", 5, 100, 20)
        general_form.addRow("Number of Iterations:", self.iter_input)
        general_form.addRow("Swarm Size:", self.pop_input)
        main_layout.addLayout(general_form)

        advanced_group = QGroupBox("hybird PSO/Genetic Algorithm Parameters")
        advanced_form = QFormLayout()

        self.w_start_input = self._add_dspinbox("Initial Inertia Weight", 0.1, 1.0, 0.9)
        self.w_end_input = self._add_dspinbox("Final Inertia Weight", 0.1, 1.0, 0.4)
        self.c1_input = self._add_dspinbox("Cognitive Coefficient", 0.1, 2.0, 1.5)
        self.c2_input = self._add_dspinbox("Social Coefficient", 0.1, 2.0, 1.5)
        self.mutation_rate_input = self._add_dspinbox("Mutation Rate", 0.0, 1.0, 0.1)
        self.crossover_rate_input = self._add_dspinbox("Crossover Rate", 0.0, 1.0, 0.9)

        advanced_form.addRow("Initial Inertia Weight:", self.w_start_input)
        advanced_form.addRow("Final Inertia Weight:", self.w_end_input)
        advanced_form.addRow("Cognitive Coefficient:", self.c1_input)
        advanced_form.addRow("Social Coefficient:", self.c2_input)
        advanced_form.addRow("Mutation Rate:", self.mutation_rate_input)
        advanced_form.addRow("Crossover Rate:", self.crossover_rate_input)

        advanced_group.setLayout(advanced_form)
        main_layout.addWidget(advanced_group)

        combo_layout = QHBoxLayout()

        self.mut_combo = QComboBox()
        self.mut_combo.addItems(["WGWRGM", "random_reinitialization_M", "swap_class_assignments_M", "field_mutation"])
        combo_layout.addWidget(QLabel("Mutation Type:"))
        combo_layout.addWidget(self.mut_combo)

        self.cross_combo = QComboBox()
        self.cross_combo.addItems(["Single Point", "Two Point", "Uniform", "Conflict Aware", "sector_based"])
        combo_layout.addWidget(QLabel("Crossover Type:"))
        combo_layout.addWidget(self.cross_combo)

        self.Selection_combo = QComboBox()
        self.Selection_combo.addItems(["Ranked", "Tournament"])
        combo_layout.addWidget(QLabel("Selection Type:"))
        combo_layout.addWidget(self.Selection_combo)

        main_layout.addLayout(combo_layout)

        self.run_button = QPushButton("Run Optimization")
        self.run_button.clicked.connect(self.run_optimization)
        main_layout.addWidget(self.run_button)
        self.run_button.setStyleSheet("background-color: lightblue; font-size: 16px;")
        self.result_table = QTableWidget()
        main_layout.addWidget(self.result_table)

        window_layout = QVBoxLayout()
        window_layout.addWidget(scroll)
        self.setLayout(window_layout)

    def _add_spinbox(self, label, min_val, max_val, default):
        box = QSpinBox()
        box.setRange(min_val, max_val)
        box.setValue(default)
        return box

    def _add_dspinbox(self, label, min_val, max_val, default):
        box = QDoubleSpinBox()
        box.setDecimals(2)
        box.setRange(min_val, max_val)
        box.setSingleStep(0.1)
        box.setValue(default)
        return box
    
    def run_optimization(self):
        iterations = self.iter_input.value()
        population_size = self.pop_input.value()
        mutation_type = self.mut_combo.currentText()
        crossover_type = self.cross_combo.currentText()
        Selection_Type = self.Selection_combo.currentText()
        w_start = self.w_start_input.value()
        w_end = self.w_end_input.value()
        c1 = self.c1_input.value()
        c2 = self.c2_input.value()
        mutation_rate = self.mutation_rate_input.value()
        crossover_rate = self.crossover_rate_input.value()

        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")

        self.thread = PSOThread(iterations, population_size, mutation_type, crossover_type, Selection_Type,
                                w_start, c1, c2, w_end, mutation_rate, crossover_rate)
        self.thread.finished.connect(self.on_finished)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def on_finished(self, best_schedule, best_fitness, global_fitness_overtime):
        self.run_button.setEnabled(True)
        self.run_button.setText("Run Optimization")
        QMessageBox.information(self, "Optimization Complete", f"Best Fitness: {best_fitness:.4f}")
        self.display_schedule(best_schedule)
        self.plot_window = PlotWindow(global_fitness_overtime)
        self.plot_window.show()


    def on_error(self, error_message):
        self.run_button.setEnabled(True)
        self.run_button.setText("Run Optimization")
        QMessageBox.critical(self, "Error", error_message)

    def display_schedule(self, schedule):
        if not schedule:
            return

        self.result_table.clear()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["Course", "Time Slot", "Room", "Lecturer"])
        self.result_table.setRowCount(len(schedule))

        for row_idx, gene in enumerate(schedule):
            self.result_table.setItem(row_idx, 0, QTableWidgetItem(str(gene.get_course().get_name())))
            self.result_table.setItem(row_idx, 1, QTableWidgetItem(str(gene.get_meetingTime().get_time())))
            self.result_table.setItem(row_idx, 2, QTableWidgetItem(str(gene.get_room().get_number())))
            self.result_table.setItem(row_idx, 3, QTableWidgetItem(str(gene.get_instructor().get_name())))

        self.result_table.setColumnWidth(0, 150)
        self.result_table.setColumnWidth(1, 200)
        self.result_table.setColumnWidth(2, 150)
        self.result_table.setColumnWidth(3, 150)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimetableOptimizerApp()
    window.show()
    sys.exit(app.exec_())
