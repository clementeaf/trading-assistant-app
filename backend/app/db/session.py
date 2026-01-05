"""
Configuración de sesión de base de datos
"""
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config.settings import get_settings

settings = get_settings()

# URL de conexión a la base de datos
DATABASE_URL: Optional[str] = (
    settings.database_url
    if hasattr(settings, "database_url") and settings.database_url
    else None
)

# Si no hay DATABASE_URL configurado, no crear engine (modo sin DB)
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=settings.stage == "dev",
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None  # type: ignore
    SessionLocal = None  # type: ignore


def get_db() -> Generator[Optional[Session], None, None]:
    """
    Dependency para obtener sesión de base de datos
    @yields Sesión de base de datos o None si no está configurada
    """
    if SessionLocal is None:
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

