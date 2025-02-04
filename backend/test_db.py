import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import add_task, get_all_tasks, mark_task_complete

# Add tasks
task1 = add_task("Complete Python Project", priority=3)
task2 = add_task("Write Documentation", priority=2)

# Retrieve all tasks
tasks = get_all_tasks()
for task in tasks:
    print(f"Task {task.id}: {task.title} (Priority: {task.priority}) - Completed: {task.completed}")

# Mark a task as complete
mark_task_complete(task1.id)