import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import add_task, get_all_tasks, mark_task_complete
from backend.utils import filter_tasks, sort_tasks, format_tasks

# Add tasks
task1 = add_task("Complete Python Project", priority=3)
task2 = add_task("Write Documentation", priority=2)
task3 = add_task("Read Research Papers", priority=1)
task4 = add_task("Prepare Presentation", priority=2)

# Retrieve all tasks
tasks = get_all_tasks()

print("\nAll Tasks:")
print("\n".join(format_tasks(tasks)))

# Filter only completed tasks
completed_tasks = filter_tasks(tasks, status=True)
print("\nCompleted Tasks:")
print("\n".join(format_tasks(completed_tasks)))

# Filter high-priority tasks
high_priority_tasks = filter_tasks(tasks, priority=3)
print("\nHigh Priority Tasks:")
print("\n".join(format_tasks(high_priority_tasks)))

# Sort tasks by priority
sorted_tasks = sort_tasks(tasks, key="priority", reverse=True)
print("\nSorted Tasks (By Priority, Descending):")
print("\n".join(format_tasks(sorted_tasks)))

# Mark a task as completed and check again
mark_task_complete(task1.id)
tasks = get_all_tasks()
completed_tasks = filter_tasks(tasks, status=True)
print("\nCompleted Tasks After Marking:")
print("\n".join(format_tasks(completed_tasks)))
