import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.database import (
    SessionLocal,
    Task,
    add_task,
    get_all_tasks,
    mark_task_complete,
)
from backend.utils import sort_tasks, filter_tasks


class TestToDoListManager(unittest.TestCase):

    def setUp(self):
        """Set up test environment"""
        # Create a session
        db = SessionLocal()

        # Clear all existing tasks before each test
        db.query(Task).delete()
        db.commit()

        # Add fresh tasks
        self.task1 = add_task("Write tests", priority=2)
        self.task2 = add_task("Fix bugs", priority=1)
        self.task3 = add_task("Optimize code", priority=3)

        # Close the session after setup
        db.close()

    def test_add_task(self):
        """Test if tasks are added correctly"""
        tasks = get_all_tasks()
        self.assertEqual(len(tasks), 3)

    def test_mark_task_complete(self):
        """Test if a task can be marked as complete"""
        mark_task_complete(self.task1.id)
        tasks = get_all_tasks()
        completed_task = next(task for task in tasks if task.id == self.task1.id)
        self.assertTrue(completed_task.completed)

    def test_sort_tasks(self):
        """Test sorting functionality"""
        tasks = get_all_tasks()
        sorted_tasks = sort_tasks(tasks, key="priority", reverse=True)
        self.assertEqual(
            sorted_tasks[0].title, "Optimize code"
        )  # Highest priority first

    def test_filter_tasks(self):
        """Test filtering completed tasks"""
        mark_task_complete(self.task1.id)
        tasks = get_all_tasks()
        completed_tasks = filter_tasks(tasks, completed=True)
        self.assertEqual(len(completed_tasks), 1)
        self.assertEqual(completed_tasks[0].title, "Write tests")

    def tearDown(self):
        """Clean up database after each test"""
        db = SessionLocal()
        db.query(Task).delete()
        db.commit()
        db.close()


if __name__ == "__main__":
    unittest.main()
