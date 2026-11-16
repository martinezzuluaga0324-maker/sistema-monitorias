"""Configuración. Los valores secretos se leen del archivo .env (ver .env.example)."""
import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-solo-para-desarrollo")
    DATABASE = os.getenv("DATABASE", os.path.join(BASE_DIR, "monitorias.db"))
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
