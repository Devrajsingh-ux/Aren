"""
Database schema definitions for AREN
This module defines all database tables using SQLAlchemy ORM
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class SystemInfo(Base):
    """System and creator information"""
    __tablename__ = 'system_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    category = Column(String(50))  # e.g., 'creator', 'system', etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    """User profile information"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(100))
    device_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    prompts = relationship("Prompt", back_populates="user")
    memories = relationship("Memory", back_populates="user")
    tasks = relationship("Task", back_populates="user")

class Prompt(Base):
    """Store unique user prompts"""
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    language = Column(String(50))

    # Relationships
    user = relationship("User", back_populates="prompts")
    responses = relationship("Response", back_populates="prompt")

class Response(Base):
    """Store responses for prompts"""
    __tablename__ = 'responses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(Integer, ForeignKey('prompts.id'))
    text = Column(Text, nullable=False)
    language = Column(String(50))
    used_count = Column(Integer, default=0)  # Track how many times this response was used
    last_used = Column(DateTime)  # When was this response last used
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    prompt = relationship("Prompt", back_populates="responses")

class Memory(Base):
    """Long-term memory storage"""
    __tablename__ = 'memory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    note = Column(Text, nullable=False)
    context = Column(String(100))  # Category/context of the memory
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration

    # Relationship
    user = relationship("User", back_populates="memories")

class Task(Base):
    """Tasks and reminders"""
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    task = Column(Text, nullable=False)
    due_date = Column(DateTime)
    is_done = Column(Boolean, default=False)
    priority = Column(Integer, default=1)  # 1=Low, 2=Medium, 3=High
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationship
    user = relationship("User", back_populates="tasks") 