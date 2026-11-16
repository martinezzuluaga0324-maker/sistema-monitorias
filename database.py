"""Conexión a la base de datos SQLite.

Flask crea una conexión por petición (g.db) y la cierra al terminar.
"""
import sqlite3
from flask import g, current_app


def get_db():
    """Devuelve la conexión de esta petición; la crea si todavía no existe."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row          # permite leer columnas por nombre: fila["nombre"]
        g.db.execute("PRAGMA foreign_keys = ON")  # SQLite no valida llaves foráneas si no se activa
    return g.db


def close_db(_error=None):
    """Cierra la conexión al terminar la petición."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
