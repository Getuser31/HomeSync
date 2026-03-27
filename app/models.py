from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


class HouseUser(Base):
    __tablename__ = "house_users"

    house_id = Column(Integer, ForeignKey("houses.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)


class TaskLifeUser(Base):
    __tablename__ = "task_life_users"

    task_life_id = Column(Integer, ForeignKey("task_lives.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)


class House(Base):
    __tablename__ = "houses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    invite_code = Column(String, unique=True)

    tasks = relationship("Task", back_populates="house")
    users = relationship("User", secondary="house_users", back_populates="houses")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    weight = Column(Integer)

    house_id = Column(Integer, ForeignKey("houses.id"))
    house = relationship("House", back_populates="tasks")

    task_lives = relationship("TaskLife", back_populates="task")


class TaskRecurrence(Base):
    __tablename__ = "task_recurrences"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    frequency_days = Column(Integer)

    task_lives = relationship("TaskLife", back_populates="recurrence")


class TaskLife(Base):
    __tablename__ = "task_lives"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    recurrence_id = Column(Integer, ForeignKey("task_recurrences.id"))

    task = relationship("Task", back_populates="task_lives")
    recurrence = relationship("TaskRecurrence", back_populates="task_lives")
    assigned_users = relationship("User", secondary="task_life_users")
    completions = relationship("TaskCompletion", back_populates="task_life")


class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id = Column(Integer, primary_key=True)
    task_life_id = Column(Integer, ForeignKey("task_lives.id"))
    user_who_completed_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    completed_at = Column(DateTime)
    period_key = Column(String)

    task_life = relationship("TaskLife", back_populates="completions")
    user_who_completed = relationship("User")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class RoleHouseUser(Base):
    __tablename__ = "role_house_users"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    house_id = Column(Integer, ForeignKey("houses.id"), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "house_id", name="uq_role_house_user"),)

    role = relationship("Role")
    house = relationship("House")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    houses = relationship("House", secondary="house_users", back_populates="users")
    role_house_users = relationship("RoleHouseUser", foreign_keys="RoleHouseUser.user_id", passive_deletes=True)
