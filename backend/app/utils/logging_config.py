"""
Configuración de logging estructurado para la aplicación
"""
import logging
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any


class StructuredFormatter(logging.Formatter):
    """
    Formatter para logging estructurado en JSON
    Facilita el parsing en sistemas de monitoring (ELK, Datadog, etc.)
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formatea el log record como JSON estructurado
        
        Args:
            record: Log record a formatear
            
        Returns:
            str: JSON string del log
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Agregar exception info si existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Agregar contexto extra si existe
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra
        
        # Agregar request_id si está disponible (útil para tracing)
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        return json.dumps(log_data)


class SimpleFormatter(logging.Formatter):
    """Formatter simple y legible para desarrollo"""
    
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging(level: Optional[str] = None, structured: bool = False) -> None:
    """
    Configura el sistema de logging de la aplicación
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        structured: Si True, usa formato JSON estructurado (para producción)
    """
    log_level = getattr(logging, level.upper() if level else "INFO", logging.INFO)
    
    # Elegir formatter según entorno
    formatter = StructuredFormatter() if structured else SimpleFormatter()
    
    # Handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]
    
    # Silenciar logs de librerías externas (solo warnings+)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Log de inicio
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured: level={level or 'INFO'}, "
        f"structured={structured}, handlers={len(root_logger.handlers)}"
    )


