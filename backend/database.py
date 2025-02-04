from sqlalchemy.orm import Session
from backend.models import Task, SessionLocal

def get_db():
    """Create a new database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_task(title, priority=1):
    """Add a new task to the database"""
    db = SessionLocal()
    new_task = Task(title=title, priority=priority)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    db.close()
    return new_task

def get_all_tasks():
    """Retrieve all tasks from the database"""
    db = SessionLocal()
    tasks = db.query(Task).all()
    db.close()
    return tasks

def mark_task_complete(task_id):
    """Mark a task as completed"""
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.completed = True
        db.commit()
    db.close()