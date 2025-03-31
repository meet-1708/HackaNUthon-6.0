from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Inventory Model
class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    quantity = Column(Float)  # Amount available
    unit = Column(String)
    price_per_unit = Column(Float)
    expiration_date = Column(Date, nullable=True)

# Recipe Model
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    ingredients = Column(String)  # Store as comma-separated names
    instructions = Column(String)
    estimated_cost = Column(Float, default=0)
