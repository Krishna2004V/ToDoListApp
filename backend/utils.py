from backend.database import get_all_tasks


def filter_tasks(tasks, completed=None, priority=None):
    """
    Filter tasks based on completed status (True/False) and priority (1, 2, 3).
    Uses the `filter` function for functional programming.
    """
    return list(
        filter(
            lambda task: (completed is None or task.completed == completed)
            and (priority is None or task.priority == priority),
            tasks,
        )
    )


def sort_tasks(tasks, key="priority", reverse=False):
    """
    Sort tasks based on a given key (priority or title).
    Uses the `sorted` function with a lambda key.
    """
    return sorted(tasks, key=lambda task: getattr(task, key), reverse=reverse)


def format_tasks(tasks):
    """
    Format task details using list comprehension.
    """
    return [
        f"Task {task.id}: {task.title} (Priority: {task.priority}) - Completed: {task.completed}"
        for task in tasks
    ]
