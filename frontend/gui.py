import sys
import os
import json
import winreg

# Add the parent directory (ToDoListApp) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QDateEdit,
    QHeaderView,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import QFile, QTimer, QDate
from backend.database import (
    add_task,
    get_all_tasks,
    mark_task_complete,
    delete_task,
    clear_all_tasks,
)
from backend.utils import sort_tasks, format_tasks


class ToDoApp(QWidget):
    """Main GUI Application for the To-Do List Manager"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("To-Do List Manager")
        self.setGeometry(200, 200, 800, 600)  # Increased size for better layout
        self.setMinimumSize(800, 600)  # Prevents the window from becoming too small
        self.dark_mode = self.is_windows_dark_mode()
        self.apply_theme()
        self.initUI()

        self.theme_timer = QTimer(self)
        self.theme_timer.timeout.connect(self.check_theme_update)
        self.theme_timer.start(3000)

    def check_theme_update(self):
        current_mode = self.is_windows_dark_mode()
        if current_mode != self.dark_mode:
            self.dark_mode = current_mode
            self.apply_theme()

    def apply_theme(self):
        """Apply consistent dark or light mode styling throughout the application"""
        if self.is_windows_dark_mode():
            theme_style = """
                QWidget { background-color: #2E2E2E; color: white; }

                QPushButton {
                    background-color: #444; 
                    color: white;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid #666;
                }
                QPushButton:hover { background-color: #555; }
                QPushButton:pressed { background-color: #666; }
                QPushButton#delete_task_button { background-color: #D9534F; }
                QPushButton#delete_task_button:hover { background-color: #C9302C; }
                QPushButton#complete_task_button { background-color: #5CB85C; }
                QPushButton#complete_task_button:hover { background-color: #4CAE4C; }

                QTableWidget {
                    background-color: #3A3A3A;
                    color: white;
                    gridline-color: #555;
                    selection-background-color: #555;
                }
                QHeaderView::section {
                    background-color: #444;
                    padding: 5px;
                    font-weight: bold;
                    border: 1px solid #666;
                }

                QComboBox, QDateEdit, QLineEdit {
                    background-color: #3A3A3A;
                    color: white;
                    border-radius: 6px;
                    padding: 6px;
                    border: 1px solid #666;
                    font-size: 14px;
                }
                QComboBox:hover, QDateEdit:hover, QLineEdit:hover { border: 1px solid #888; }
                QComboBox QAbstractItemView {
                    background-color: #3A3A3A;
                    selection-background-color: #555;
                    border-radius: 6px;
                }
                QLineEdit:focus {
                    border: 2px solid #1DB954;
                    background-color: #444;
                }
            """
        else:
            theme_style = """
                QWidget { background-color: #F5F5F5; color: black; }

                QPushButton {
                    background-color: #E0E0E0; 
                    color: black;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 14px;
                    border: 1px solid #BDBDBD;
                }
                QPushButton:hover { background-color: #D6D6D6; }
                QPushButton:pressed { background-color: #BDBDBD; }
                QPushButton#delete_task_button { background-color: #FF6B6B; }
                QPushButton#delete_task_button:hover { background-color: #FF3B3B; }
                QPushButton#complete_task_button { background-color: #4CAF50; }
                QPushButton#complete_task_button:hover { background-color: #45A049; }

                QTableWidget {
                    background-color: white;
                    color: black;
                    gridline-color: #CCC;
                    selection-background-color: #D6D6D6;
                }
                QHeaderView::section {
                    background-color: #E0E0E0;
                    padding: 5px;
                    font-weight: bold;
                    border: 1px solid #BDBDBD;
                }

                QComboBox, QDateEdit, QLineEdit {
                    background-color: #FFFFFF;
                    color: black;
                    border-radius: 6px;
                    padding: 6px;
                    border: 1px solid #BDBDBD;
                    font-size: 14px;
                }
                QComboBox:hover, QDateEdit:hover, QLineEdit:hover { border: 1px solid #888; }
                QComboBox QAbstractItemView {
                    background-color: #F5F5F5;
                    selection-background-color: #D6D6D6;
                    border-radius: 6px;
                }
                QLineEdit:focus {
                    border: 2px solid #1DB954;
                    background-color: #F0F0F0;
                }
            """

        self.setStyleSheet(theme_style)

        # Apply the theme to individual widgets if necessary
        if hasattr(self, "search_bar"):
            self.search_bar.setStyleSheet(theme_style)

    @staticmethod
    def is_windows_dark_mode():
        try:
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(
                registry,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except:
            return False

    def initUI(self):
        layout = QVBoxLayout()

        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Enter a new task")
        layout.addWidget(self.task_input)

        self.priority_dropdown = QComboBox(self)
        self.priority_dropdown.addItems(["Low", "Medium", "High"])
        layout.addWidget(self.priority_dropdown)

        # Deadline input
        self.deadline_input = QDateEdit(self)
        self.deadline_input.setCalendarPopup(True)  # Enables calendar popup selection
        self.deadline_input.setDate(QDate.currentDate())  # Default to today
        self.deadline_input.setMinimumDate(QDate.currentDate())  # Prevent past dates
        layout.addWidget(self.deadline_input)

        self.add_task_button = QPushButton("Add Task", self)
        self.add_task_button.clicked.connect(self.add_task)
        layout.addWidget(self.add_task_button)

        self.task_table = QTableWidget(self)
        self.task_table.setColumnCount(5)  # Ensure 5 columns including Deadline
        self.task_table.setHorizontalHeaderLabels(
            ["ID", "Title", "Priority", "Status", "Deadline"]
        )
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.task_table)

        self.complete_task_button = QPushButton("Mark as Completed", self)
        self.complete_task_button.clicked.connect(self.mark_task_complete)
        layout.addWidget(self.complete_task_button)

        self.delete_task_button = QPushButton("Delete Task", self)
        self.delete_task_button.clicked.connect(self.delete_task)
        layout.addWidget(self.delete_task_button)

        self.sort_dropdown = QComboBox(self)
        self.sort_dropdown.addItems(
            ["Priority (High to Low)", "Priority (Low to High)", "Title (A-Z)"]
        )
        self.sort_dropdown.currentIndexChanged.connect(self.update_task_list)
        layout.addWidget(self.sort_dropdown)

        self.save_tasks_button = QPushButton("Save Tasks", self)
        self.save_tasks_button.clicked.connect(self.save_tasks)
        layout.addWidget(self.save_tasks_button)

        self.clear_all_tasks_button = QPushButton("Clear All Tasks", self)
        self.clear_all_tasks_button.clicked.connect(self.clear_all_tasks)
        layout.addWidget(self.clear_all_tasks_button)

        self.load_tasks_button = QPushButton("Load Tasks", self)
        self.load_tasks_button.clicked.connect(self.load_tasks)
        layout.addWidget(self.load_tasks_button)

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("🔍 Search tasks...")
        self.search_bar.setStyleSheet(
            """
            QLineEdit {
                background-color: #3A3A3A; /* Dark background */
                color: white;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #1DB954; /* Green border when focused */
                background-color: #444;
            }
        """
        )
        self.search_bar.textChanged.connect(self.filter_tasks)
        layout.addWidget(self.search_bar)

        self.setLayout(layout)
        self.update_task_list()

        self.complete_task_button.setObjectName("complete_task_button")
        self.delete_task_button.setObjectName("delete_task_button")

        # Set resize mode for all columns to Stretch
        header = self.task_table.horizontalHeader()
        for i in range(self.task_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        # Resize columns to fit the content automatically
        self.task_table.resizeColumnsToContents()

    def filter_tasks(self):
        """Filter tasks based on user input in the search bar."""
        search_text = self.search_bar.text().strip().lower()

        for row in range(self.task_table.rowCount()):
            title_item = self.task_table.item(row, 1)  # Title column
            if title_item:
                title = title_item.text().strip().lower()
                self.task_table.setRowHidden(row, search_text not in title)

    def add_task(self):
        title = self.task_input.text().strip()
        priority = self.priority_dropdown.currentIndex() + 1
        deadline = self.deadline_input.date().toString("yyyy-MM-dd")  # Format deadline

        if title:
            add_task(title, priority, deadline)  # Pass deadline to database
            self.task_input.clear()
            self.update_task_list()
        else:
            QMessageBox.warning(self, "Input Error", "Task title cannot be empty!")

    def update_task_list(self):
        tasks = get_all_tasks()
        sort_index = self.sort_dropdown.currentIndex()
        sort_key, reverse = (
            ("priority", True)
            if sort_index == 0
            else ("priority", False) if sort_index == 1 else ("title", False)
        )
        sorted_tasks = sort_tasks(tasks, key=sort_key, reverse=reverse)

        self.task_table.setRowCount(len(sorted_tasks))
        self.task_table.setColumnCount(5)  # Ensure there are 5 columns now
        self.task_table.setHorizontalHeaderLabels(
            ["ID", "Title", "Priority", "Status", "Deadline"]
        )  # Updated

        for row, task in enumerate(sorted_tasks):
            self.task_table.setItem(row, 0, QTableWidgetItem(str(task.id)))
            self.task_table.setItem(row, 1, QTableWidgetItem(task.title))
            self.task_table.setItem(row, 2, QTableWidgetItem(str(task.priority)))

            # Status Column (Completed or Pending)
            status_text = "Completed" if task.completed else "Pending"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(
                QColor("green") if task.completed else QColor("red")
            )
            self.task_table.setItem(row, 3, status_item)

            # Handle Missing or Invalid Deadlines
            deadline_item = QTableWidgetItem("N/A")  # Default value
            if task.deadline and isinstance(task.deadline, str):
                deadline_date = QDate.fromString(
                    task.deadline, "yyyy-MM-dd"
                )  # Convert from DB format
                if deadline_date.isValid():
                    formatted_deadline = deadline_date.toString(
                        "dd-MM-yyyy"
                    )  # Convert to desired format
                    deadline_item.setText(formatted_deadline)

                    # Apply Color Coding for Deadlines
                    today = QDate.currentDate()
                    if deadline_date < today:
                        deadline_item.setForeground(QColor("red"))  # Overdue
                    elif deadline_date <= today.addDays(6):
                        deadline_item.setForeground(QColor("orange"))  # Due soon
                    else:
                        deadline_item.setForeground(QColor("green"))  # Safe

            self.task_table.setItem(row, 4, deadline_item)

    def mark_task_complete(self):
        selected_row = self.task_table.currentRow()
        if selected_row >= 0:
            task_id = int(self.task_table.item(selected_row, 0).text())
            mark_task_complete(task_id)
            self.update_task_list()
        else:
            QMessageBox.warning(
                self, "Selection Error", "Select a task to mark as completed!"
            )

    def save_tasks(self):
        """Save tasks to a JSON file"""
        filename = "tasks.json"
        tasks = get_all_tasks()
        task_data = [
            {
                "id": task.id,
                "title": task.title,
                "priority": task.priority,
                "completed": task.completed,
                "deadline": (
                    QDate.fromString(task.deadline, "yyyy-MM-dd").toString("dd-MM-yyyy")
                    if task.deadline
                    else "N/A"
                ),
            }
            for task in tasks
        ]

        with open(filename, "w") as file:
            json.dump(task_data, file, indent=4)

        QMessageBox.information(
            self, "Saved", f"Tasks saved successfully to {filename}!"
        )

    def load_tasks(self):
        """Load tasks from a JSON file without duplicating existing ones"""
        filename = "tasks.json"
        if not os.path.exists(filename):
            QMessageBox.warning(self, "Error", f"No saved tasks found in {filename}!")
            return

        try:
            with open(filename, "r") as file:
                task_data = json.load(file)

            existing_tasks = {task.title for task in get_all_tasks()}
            new_tasks = []

            for task in task_data:
                if task["title"] not in existing_tasks:
                    # Convert "DD-MM-YYYY" back to "YYYY-MM-DD" before adding to DB
                    deadline_qdate = QDate.fromString(
                        task.get("deadline", ""), "dd-MM-yyyy"
                    )
                    deadline_str = (
                        deadline_qdate.toString("yyyy-MM-dd")
                        if deadline_qdate.isValid()
                        else None
                    )

                    add_task(task["title"], task["priority"], deadline_str)
                    new_tasks.append(task)

            if new_tasks:
                self.update_task_list()
                QMessageBox.information(
                    self, "Loaded", f"Added {len(new_tasks)} new tasks from {filename}!"
                )
            else:
                QMessageBox.information(self, "Loaded", "No new tasks to add.")

        except json.JSONDecodeError:
            QMessageBox.warning(
                self, "Error", f"Failed to read {filename}! File might be corrupted."
            )

    def delete_task(self):
        """Delete the selected task from the database"""
        selected_row = self.task_table.currentRow()
        if selected_row >= 0:
            task_id = int(self.task_table.item(selected_row, 0).text())
            delete_task(task_id)
            self.update_task_list()
        else:
            QMessageBox.warning(self, "Selection Error", "Select a task to delete!")

    def clear_all_tasks(self):
        """Clear all tasks from the database and update the UI"""
        confirmation = QMessageBox.question(
            self,
            "Clear All Tasks",
            "Are you sure you want to delete all tasks?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if confirmation == QMessageBox.Yes:
            clear_all_tasks()  # Ensure this function is imported from backend.database
            self.update_task_list()
            QMessageBox.information(self, "Cleared", "All tasks have been deleted.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec())
