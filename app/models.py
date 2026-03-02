from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base


class HouseUser(Base):
    __tablename__ = "house_users"

    house_id = Column(Integer, ForeignKey("houses.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


class House(Base):
    __tablename__ = "houses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    invite_code = Column(String, unique=True)

    tasks = relationship("Task", back_populates="house")
    users = relationship("User", secondary="house_users", back_populates="houses")


class TaskCategory(Base):
    __tablename__ = "task_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    tasks = relationship("Task", back_populates="category")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)

    house_id = Column(Integer, ForeignKey("houses.id"))
    house = relationship("House", back_populates="tasks")

    category_id = Column(Integer, ForeignKey("task_categories.id"))
    category = relationship("TaskCategory", back_populates="tasks")

    assignments = relationship("Assignment", back_populates="task")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    houses = relationship("House", secondary="house_users", back_populates="users")
    assignments = relationship("Assignment", back_populates="user")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="assignments")

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="assignments")

    due_date = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False)
