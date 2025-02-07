from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Database Setup
DATABASE_URL = "sqlite:///tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

# Task Model
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    priority = Column(Integer, default=1)
    completed = Column(Boolean, default=False)

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Database Functions
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

def delete_task(task_id: int):
    """Delete a task from the database by its ID"""
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        db.close()
        return True
    db.close()
    return False