from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")
DATA_DB_PATH = os.path.join(DB_DIR, "data.db")

os.makedirs(DB_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, index=True)
    feature1 = Column(Float)
    feature2 = Column(Float)
    target = Column(Integer)

Base.metadata.create_all(bind=engine)
