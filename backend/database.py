from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Database Setup
DATABASE_URL = "sqlite:///tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()


# Task Model
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    priority = Column(Integer, default=1)
    completed = Column(Boolean, default=False)
    deadline = Column(String, nullable=True)  # Add this line


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


# Update add_task function to store deadlines
def add_task(title, priority, deadline=None):
    with SessionLocal() as db:  # Fix `Session` to `SessionLocal`
        new_task = Task(title=title, priority=priority, deadline=deadline)
        db.add(new_task)
        db.commit()


def get_all_tasks():
    """Fetch all tasks from the database including their completion status."""
    with SessionLocal() as db:
        return db.query(Task).all()


def mark_task_complete(task_id):
    """Mark a task as completed"""
    with SessionLocal() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.completed = True
            db.commit()


def delete_task(task_id: int):
    """Delete a task from the database by its ID"""
    with SessionLocal() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            db.delete(task)
            db.commit()
            return True
        return False


def clear_all_tasks():
    """Delete all tasks from the database"""
    with SessionLocal() as db:
        db.query(Task).delete()
        db.commit()
