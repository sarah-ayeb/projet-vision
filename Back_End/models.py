from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

# Create base for models
Base = declarative_base()

# Modèle SQLAlchemy pour la table "users"
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


# Modèle SQLAlchemy pour la table "products"
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=True)
    reference = Column(String(255), nullable=True)
    price = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, default=1)
    barcode = Column(String(32), nullable=False)
    product_name = Column(String(255), nullable=True)
    search_date = Column(DateTime, default=datetime.datetime.utcnow)
    total_results = Column(Integer, nullable=False)
    results = Column(Text, nullable=False)  # Store as JSON string


# Modèle SQLAlchemy pour la table "sites"
class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String(255), unique=True, nullable=False)
    search_url = Column(String(500), nullable=False)
    selectors = Column(Text, nullable=False)  # Store as JSON string
    logo_url = Column(String(500), nullable=True)  # Store logo URL
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)