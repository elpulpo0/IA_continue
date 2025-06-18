from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from modules.database.config import USERS_DATABASE_URL

# Separate Base declarations for each database
UsersBase = declarative_base()

def create_session(database_url: str):
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

# User database session and engine
users_engine, UsersSessionLocal = create_session(USERS_DATABASE_URL)