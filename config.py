"""Configuración. Los valores secretos se leen del archivo .env (ver .env.example)."""
import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# En Vercel el disco es de solo lectura salvo /tmp, así que allí la base de datos vive en /tmp
# (se reinicia en cada arranque en frío; sirve para demostración, no para guardar datos reales).
_BD_POR_DEFECTO = "/tmp/monitorias.db" if os.getenv("VERCEL") else os.path.join(BASE_DIR, "monitorias.db")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-solo-para-desarrollo")
    DATABASE = os.getenv("DATABASE", _BD_POR_DEFECTO)
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
