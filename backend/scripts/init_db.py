"""
Script para inicializar la base de datos
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.models import Base
from app.db.session import engine


def init_db() -> None:
    """
    Crea todas las tablas en la base de datos
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()

