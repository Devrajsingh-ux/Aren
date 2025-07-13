"""
Database Configuration and Connection Management for AREN
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
from utils.logging_utils import logger
from utils.database_schema import Base, User, Prompt, Response, Memory, Task, SystemInfo
from contextlib import contextmanager
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.engine = None
            self.Session = None
            self.initialize_connection()
            self.initialized = True

    def initialize_connection(self):
        """Create database connection using environment variables"""
        try:
            db_host = 'localhost'
            db_port = '5432'
            db_user = 'aren'
            db_password = 'aren_password'
            db_name = 'aren_conversations'

            connection_string = (
                f"postgresql://{db_user}:{db_password}@"
                f"{db_host}:{db_port}/{db_name}"
            )

            # Configure connection pooling
            self.engine = create_engine(
                connection_string,
                echo=True,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600
            )

            # Add connection pool event listeners
            @event.listens_for(self.engine, 'connect')
            def receive_connect(dbapi_connection, connection_record):
                logger.info("New database connection established")

            @event.listens_for(self.engine, 'checkout')
            def receive_checkout(dbapi_connection, connection_record, connection_proxy):
                logger.debug("Database connection checked out from pool")

            @event.listens_for(self.engine, 'checkin')
            def receive_checkin(dbapi_connection, connection_record):
                logger.debug("Database connection returned to pool")

            # Create all tables
            Base.metadata.create_all(self.engine)
            
            # Create thread-safe session factory
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            
            # Test connection
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                logger.info("Database connection test successful!")
            
            logger.info("Database connection initialized successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error initializing database connection: {e}")
            raise

    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def save_conversation(self, user_id, prompt_text, response_text, language="en"):
        """Save a conversation exchange to the database"""
        with self.get_session() as session:
            try:
                # Check if prompt exists
                prompt = session.query(Prompt).filter_by(
                    user_id=user_id,
                    text=prompt_text
                ).first()
                
                if not prompt:
                    prompt = Prompt(
                        user_id=user_id,
                        text=prompt_text,
                        language=language
                    )
                    session.add(prompt)
                    session.flush()  # Get the prompt ID
                
                # Check if response exists for this prompt
                response = session.query(Response).filter_by(
                    prompt_id=prompt.id,
                    text=response_text
                ).first()
                
                if response:
                    # Update existing response
                    response.used_count += 1
                    response.last_used = datetime.utcnow()
                else:
                    # Create new response
                    response = Response(
                        prompt_id=prompt.id,
                        text=response_text,
                        language=language,
                        used_count=1,
                        last_used=datetime.utcnow()
                    )
                    session.add(response)
                
                logger.info("Conversation saved to database")
                return True
            except SQLAlchemyError as e:
                logger.error(f"Error saving conversation: {e}")
                raise

    def get_or_create_user(self, device_id, name=None):
        """Get existing user or create new one"""
        with self.get_session() as session:
            try:
                user = session.query(User).filter_by(device_id=device_id).first()
                if not user:
                    user = User(device_id=device_id, name=name)
                    session.add(user)
                    session.commit()  # Commit to get the ID
                return user.id  # Return just the ID instead of the user object
            except SQLAlchemyError as e:
                logger.error(f"Error getting/creating user: {e}")
                raise

    def add_memory(self, user_id, note, context, expires_at=None):
        """Add a memory entry for a user"""
        with self.get_session() as session:
            try:
                memory = Memory(
                    user_id=user_id,
                    note=note,
                    context=context,
                    expires_at=expires_at
                )
                session.add(memory)
                logger.info("Memory saved to database")
                return True
            except SQLAlchemyError as e:
                logger.error(f"Error adding memory: {e}")
                raise

    def add_task(self, user_id, task, due_date, priority=1):
        """Add a task for a user"""
        with self.get_session() as session:
            try:
                task = Task(
                    user_id=user_id,
                    task=task,
                    due_date=due_date,
                    priority=priority
                )
                session.add(task)
                logger.info("Task saved to database")
                return True
            except SQLAlchemyError as e:
                logger.error(f"Error adding task: {e}")
                raise

    def get_responses_for_prompt(self, prompt_text, user_id, limit=5):
        """Get responses for a given prompt"""
        with self.get_session() as session:
            try:
                responses = session.query(Response).join(Prompt).filter(
                    Prompt.user_id == user_id,
                    Prompt.text == prompt_text
                ).order_by(Response.used_count.desc()).limit(limit).all()
                return responses
            except SQLAlchemyError as e:
                logger.error(f"Error getting responses: {e}")
                raise

    def get_memories(self, user_id):
        """Get all memories for a user"""
        with self.get_session() as session:
            try:
                memories = session.query(Memory).filter_by(
                    user_id=user_id
                ).order_by(Memory.created_at.desc()).all()
                return memories
            except SQLAlchemyError as e:
                logger.error(f"Error getting memories: {e}")
                raise

    def get_pending_tasks(self, user_id):
        """Get all pending tasks for a user"""
        with self.get_session() as session:
            try:
                tasks = session.query(Task).filter_by(
                    user_id=user_id,
                    is_done=False
                ).order_by(Task.due_date).all()
                return tasks
            except SQLAlchemyError as e:
                logger.error(f"Error getting tasks: {e}")
                raise 

    def add_system_info(self, key: str, value: str, category: str = None) -> bool:
        """Add or update system information"""
        with self.get_session() as session:
            try:
                info = session.query(SystemInfo).filter_by(key=key).first()
                if info:
                    info.value = value
                    info.category = category
                    info.updated_at = datetime.utcnow()
                else:
                    info = SystemInfo(
                        key=key,
                        value=value,
                        category=category
                    )
                    session.add(info)
                logger.info(f"System info saved: {key}")
                return True
            except SQLAlchemyError as e:
                logger.error(f"Error saving system info: {e}")
                raise

    def get_system_info(self, key: str = None, category: str = None) -> List[Dict[str, Any]]:
        """Get system information by key or category"""
        with self.get_session() as session:
            try:
                query = session.query(SystemInfo)
                if key:
                    query = query.filter_by(key=key)
                if category:
                    query = query.filter_by(category=category)
                results = query.all()
                return [
                    {
                        'key': info.key,
                        'value': info.value,
                        'category': info.category,
                        'created_at': info.created_at,
                        'updated_at': info.updated_at
                    }
                    for info in results
                ]
            except SQLAlchemyError as e:
                logger.error(f"Error getting system info: {e}")
                raise 

# Create a singleton instance to be imported by other modules
db_manager = DatabaseManager() 