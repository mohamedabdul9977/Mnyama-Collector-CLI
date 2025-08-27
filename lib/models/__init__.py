from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Create database engine
DATABASE_URL = "sqlite:///creatures.db"
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

# Base class for all models
Base = declarative_base()

# Import all models to ensure they're registered
from .models import Species, Creature, Habitat, creature_habitats

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

def get_session():
    """Get a database session"""
    return SessionLocal()