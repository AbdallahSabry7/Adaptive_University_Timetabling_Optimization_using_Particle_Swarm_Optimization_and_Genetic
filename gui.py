import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
    QSpinBox, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from main import pso_main  # Make sure your pso_main accepts (iterations, swarm_size)


class PSOThread(QThread):
    finished = pyqtSignal(object, float)
    error = pyqtSignal(str)

    def __init__(self, iterations, population_size):
        super().__init__()
        self.iterations = iterations
        self.population_size = population_size

    def run(self):
        try:
            best_schedule, best_fitness = pso_main(self.iterations, self.population_size)
            self.finished.emit(best_schedule, best_fitness)
        except Exception as e:
            self.error.emit(str(e))


class TimetableOptimizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Timetable Optimizer - PSO")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.iter_label = QLabel("Number of Iterations:")
        self.iter_input = QSpinBox()
        self.iter_input.setMinimum(10)
        self.iter_input.setMaximum(1000)
        self.iter_input.setValue(50)

        self.pop_label = QLabel("Swarm Size:")
        self.pop_input = QSpinBox()
        self.pop_input.setMinimum(5)
        self.pop_input.setMaximum(100)
        self.pop_input.setValue(10)

        layout.addWidget(self.iter_label)
        layout.addWidget(self.iter_input)
        layout.addWidget(self.pop_label)
        layout.addWidget(self.pop_input)

        self.run_button = QPushButton("Run Optimization")
        self.run_button.clicked.connect(self.run_optimization)
        layout.addWidget(self.run_button)

        self.result_table = QTableWidget()
        layout.addWidget(self.result_table)

        self.setLayout(layout)

    def run_optimization(self):
        iterations = self.iter_input.value()
        population_size = self.pop_input.value()

        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")

        self.thread = PSOThread(iterations, population_size)
        self.thread.finished.connect(self.on_finished)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def on_finished(self, best_schedule, best_fitness):
        self.run_button.setEnabled(True)
        self.run_button.setText("Run Optimization")
        QMessageBox.information(self, "Optimization Complete", f"Best Fitness: {best_fitness:.4f}")
        self.display_schedule(best_schedule)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimetableOptimizerApp()
    window.show()
    sys.exit(app.exec_())