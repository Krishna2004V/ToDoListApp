from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Base class for ORM models
Base = declarative_base()


class Task(Base):
    """Task Model - Represents a task in the database"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    priority = Column(Integer, default=1)  # 1 = Low, 2 = Medium, 3 = High
    completed = Column(Boolean, default=False)


# Database connection setup
DATABASE_URL = "sqlite:///tasks.db"  # Use PostgreSQL in production
engine = create_engine(DATABASE_URL, echo=True)  # echo=True for debugging
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create database tables if they do not exist"""
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()  # Initialize the database when this script runs
