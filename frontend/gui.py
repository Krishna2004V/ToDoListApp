import sys
import os

# Add the parent directory to sys.path so that 'backend' is recognized
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QLineEdit, QComboBox, QMessageBox
)
from backend.database import add_task, get_all_tasks, mark_task_complete
from backend.utils import filter_tasks, sort_tasks, format_tasks

class ToDoApp(QWidget):
    """Main GUI Application for the To-Do List Manager"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List Manager")
        self.setGeometry(200, 200, 400, 500)
        self.initUI()

    def initUI(self):
        """Initialize UI Components"""
        layout = QVBoxLayout()

        # Task Input Field
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Enter a new task")
        layout.addWidget(self.task_input)

        # Priority Dropdown
        self.priority_dropdown = QComboBox(self)
        self.priority_dropdown.addItems(["Low", "Medium", "High"])
        layout.addWidget(self.priority_dropdown)

        # Add Task Button
        self.add_task_button = QPushButton("Add Task", self)
        self.add_task_button.clicked.connect(self.add_task)
        layout.addWidget(self.add_task_button)

        # Task List
        self.task_list = QListWidget(self)
        layout.addWidget(self.task_list)

        # Mark Task as Complete Button
        self.complete_task_button = QPushButton("Mark as Completed", self)
        self.complete_task_button.clicked.connect(self.mark_task_complete)
        layout.addWidget(self.complete_task_button)

        # Sorting Dropdown
        self.sort_dropdown = QComboBox(self)
        self.sort_dropdown.addItems(["Priority (High to Low)", "Priority (Low to High)", "Title (A-Z)"])
        self.sort_dropdown.currentIndexChanged.connect(self.update_task_list)
        layout.addWidget(self.sort_dropdown)

        # Set Layout
        self.setLayout(layout)
        self.update_task_list()

    def add_task(self):
        """Add a new task to the database"""
        title = self.task_input.text().strip()
        priority = self.priority_dropdown.currentIndex() + 1  # Convert index to 1, 2, 3

        if title:
            add_task(title, priority)
            self.task_input.clear()
            self.update_task_list()
        else:
            QMessageBox.warning(self, "Input Error", "Task title cannot be empty!")

    def update_task_list(self):
        """Update the task list display"""
        tasks = get_all_tasks()

        # Apply Sorting
        sort_key = "priority"
        reverse = True  # Default: High Priority First

        if self.sort_dropdown.currentIndex() == 1:
            reverse = False  # Low Priority First
        elif self.sort_dropdown.currentIndex() == 2:
            sort_key = "title"
            reverse = False

        sorted_tasks = sort_tasks(tasks, key=sort_key, reverse=reverse)
        formatted_tasks = format_tasks(sorted_tasks)

        # Update List Widget
        self.task_list.clear()
        self.task_list.addItems(formatted_tasks)

    def mark_task_complete(self):
        """Mark selected task as completed"""
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_id = int(selected_item.text().split()[1])  # Extract task ID
            mark_task_complete(task_id)
            self.update_task_list()
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a task to mark as completed!")

# Run the Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec())