"""
Punto de entrada para AWS Lambda
"""
from mangum import Mangum

from app.main import app

handler = Mangum(app, lifespan="off")
