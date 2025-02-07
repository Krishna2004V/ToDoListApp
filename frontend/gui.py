import sys
import os
import json
import winreg

# Add the parent directory (ToDoListApp) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QLineEdit, 
    QComboBox, QMessageBox
)
from PySide6.QtCore import QFile, QTimer
from backend.database import add_task, get_all_tasks, mark_task_complete, delete_task, clear_all_tasks
from backend.utils import filter_tasks, sort_tasks, format_tasks

class ToDoApp(QWidget):
    """Main GUI Application for the To-Do List Manager"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List Manager")
        self.setGeometry(200, 200, 400, 500)
        self.dark_mode = self.is_windows_dark_mode()  # Store initial theme
        self.apply_theme()
        self.initUI()

        # Periodically check for theme changes
        self.theme_timer = QTimer(self)
        self.theme_timer.timeout.connect(self.check_theme_update)
        self.theme_timer.start(3000)  # Check every 3 seconds

    def check_theme_update(self):
        """Check if Windows theme changed and update the UI"""
        current_mode = self.is_windows_dark_mode()
        if current_mode != self.dark_mode:
            self.dark_mode = current_mode
            self.apply_theme()
                
    def apply_theme(self):
        """Apply Light or Dark Mode based on Windows settings"""
        if self.is_windows_dark_mode():
            dark_style = """
                QWidget {
                    background-color: #2E2E2E;
                    color: white;
                }
                QPushButton {
                    background-color: #555555;
                    color: white;
                    border: 1px solid #777777;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
                QLineEdit, QComboBox, QListWidget {
                    background-color: #444444;
                    color: white;
                    border: 1px solid #666666;
                    border-radius: 5px;
                }
            """
            self.setStyleSheet(dark_style)
        else:
            light_style = """
                QWidget {
                    background-color: #F5F5F5;
                    color: black;
                }
                QPushButton {
                    background-color: #DDDDDD;
                    color: black;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #EEEEEE;
                }
                QLineEdit, QComboBox, QListWidget {
                    background-color: white;
                    color: black;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                }
            """
            self.setStyleSheet(light_style)

    @staticmethod
    def is_windows_dark_mode():
        """Check if Windows is set to Dark Mode"""
        try:
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)  # Close the registry key after use
            return value == 0  # 0 means Dark Mode, 1 means Light Mode
        except FileNotFoundError:
            return False  # Default to Light Mode if registry key is missing
        except Exception:
            return False  # Default if any other error occurs

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

        # Delete Task Button
        self.delete_task_button = QPushButton("Delete Task", self)
        self.delete_task_button.clicked.connect(self.delete_task)
        layout.addWidget(self.delete_task_button)

        # Sorting Dropdown
        self.sort_dropdown = QComboBox(self)
        self.sort_dropdown.addItems(["Priority (High to Low)", "Priority (Low to High)", "Title (A-Z)"])
        self.sort_dropdown.currentIndexChanged.connect(self.update_task_list)
        layout.addWidget(self.sort_dropdown)

        # Save & Load Tasks Buttons
        self.save_tasks_button = QPushButton("Save Tasks", self)
        self.save_tasks_button.clicked.connect(self.save_tasks)
        layout.addWidget(self.save_tasks_button)

        # Clear All Tasks Button
        self.clear_all_tasks_button = QPushButton("Clear All Tasks", self)
        self.clear_all_tasks_button.clicked.connect(self.clear_all_tasks)
        layout.addWidget(self.clear_all_tasks_button)

        self.load_tasks_button = QPushButton("Load Tasks", self)
        self.load_tasks_button.clicked.connect(self.load_tasks)
        layout.addWidget(self.load_tasks_button)

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
        sort_index = self.sort_dropdown.currentIndex()

        sort_key = "priority"
        reverse = True  # Default: High Priority First

        if sort_index == 1:
            reverse = False  # Low Priority First
        elif sort_index == 2:
            sort_key = "title"
            reverse = False

        sorted_tasks = sort_tasks(tasks, key=sort_key, reverse=reverse)
        formatted_tasks = format_tasks(sorted_tasks)

        self.task_list.clear()
        self.task_list.addItems(formatted_tasks)

    def mark_task_complete(self):
        """Mark selected task as completed"""
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_id = int(selected_item.text().split()[1].split(":")[0])  # Extract task ID
            mark_task_complete(task_id)
            self.update_task_list()
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a task to mark as completed!")

    def delete_task(self):
        """Delete a selected task from the database"""
        selected_item = self.task_list.currentItem()
        if selected_item:
            try:
                task_id = int(selected_item.text().split()[1].split(":")[0])  # Extract task ID
                
                if delete_task(task_id):
                    QMessageBox.information(self, "Deleted", f"Task {task_id} deleted.")
                else:
                    QMessageBox.warning(self, "Error", f"Task {task_id} not found!")

                self.update_task_list()
            except ValueError:
                QMessageBox.warning(self, "Error", "Failed to extract task ID!")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a task to delete!")

    def save_tasks(self):
        """Save tasks to a JSON file"""
        filename = "tasks.json"
        tasks = get_all_tasks()
        task_data = [{"id": task.id, "title": task.title, "priority": task.priority, "completed": task.completed} for task in tasks]

        with open(filename, "w") as file:
            json.dump(task_data, file, indent=4)

        QMessageBox.information(self, "Saved", f"Tasks saved successfully to {filename}!")

    def load_tasks(self):
        """Load tasks from a JSON file"""
        filename = "tasks.json"
        if not os.path.exists(filename):
            QMessageBox.warning(self, "Error", f"No saved tasks found in {filename}!")
            return

        try:
            with open(filename, "r") as file:
                task_data = json.load(file)

            for task in task_data:
                add_task(task["title"], task["priority"])

            self.update_task_list()
            QMessageBox.information(self, "Loaded", f"Tasks loaded successfully from {filename}!")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", f"Failed to read {filename}! File might be corrupted.")

    def clear_all_tasks(self):
        """Clear all tasks from the database and update the UI"""
        confirmation = QMessageBox.question(
            self, "Clear All Tasks", "Are you sure you want to delete all tasks?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if confirmation == QMessageBox.Yes:
            clear_all_tasks()
            self.update_task_list()
            QMessageBox.information(self, "Cleared", "All tasks have been deleted.")

# Run the Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec())