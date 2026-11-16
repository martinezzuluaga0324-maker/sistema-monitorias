"""Crea la base de datos desde schema.sql y carga datos de ejemplo para la demostración.

Ejecutar una vez:  python init_db.py
(Cuidado: borra y recrea las tablas.)
"""
import os
import sqlite3
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

from config import Config

CLAVE_DEMO = "Tandem2026!"


def main():
    db = sqlite3.connect(Config.DATABASE)
    db.execute("PRAGMA foreign_keys = ON")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql"), encoding="utf-8") as f:
        db.executescript(f.read())

    h = generate_password_hash(CLAVE_DEMO)

    def usuario(nombre, codigo, correo, rol, programa):
        return db.execute(
            "INSERT INTO usuarios (nombre, codigo, correo, clave_hash, rol, programa) VALUES (?,?,?,?,?,?)",
            (nombre, codigo, correo, h, rol, programa),
        ).lastrowid

    # Personal
    bienestar = usuario("Patricia Ramírez", None, "bienestar@tandem.edu", "bienestar", "Bienestar Institucional")
    d_calc = usuario("Carlos Mejía", None, "docente.calculo@tandem.edu", "docente", "Ciencias Básicas")
    d_prog = usuario("Luisa Fernanda Torres", None, "docente.prog@tandem.edu", "docente", "Ingeniería de Sistemas")

    # Materias
    materias = {}
    for nombre, doc in [("Cálculo I", d_calc), ("Álgebra Lineal", d_calc), ("Física I", d_calc),
                        ("Programación", d_prog), ("Bases de Datos", d_prog), ("Estadística", d_calc)]:
        materias[nombre] = db.execute("INSERT INTO materias (nombre, docente_id) VALUES (?, ?)", (nombre, doc)).lastrowid

    # Monitores: (nombre, código, correo, materias, franjas)
    monitores = [
        ("Camila Rojas", "20211001", "camila@tandem.edu", ["Cálculo I", "Álgebra Lineal"], [("Lunes", "14:00", "16:00"), ("Miércoles", "10:00", "12:00")]),
        ("Andrés Pardo", "20211002", "andres@tandem.edu", ["Programación", "Bases de Datos"], [("Martes", "09:00", "11:00"), ("Jueves", "15:00", "17:00")]),
        ("Valentina Cruz", "20211003", "valentina@tandem.edu", ["Física I"], [("Lunes", "08:00", "10:00"), ("Viernes", "13:00", "15:00")]),
        ("Daniela Ortiz", "20211004", "daniela@tandem.edu", ["Estadística", "Cálculo I"], [("Martes", "14:00", "16:00"), ("Jueves", "10:00", "12:00")]),
    ]
    ids_mon = []
    for nombre, cod, correo, mats, franjas in monitores:
        mid = usuario(nombre, cod, correo, "monitor", "Ingeniería de Sistemas")
        ids_mon.append(mid)
        for m in mats:
            db.execute("INSERT INTO monitor_materias VALUES (?, ?)", (mid, materias[m]))
        for dia, ini, fin in franjas:
            db.execute("INSERT INTO disponibilidades (monitor_id, dia, hora_inicio, hora_fin) VALUES (?,?,?,?)", (mid, dia, ini, fin))

    # Estudiantes e inscripciones
    estudiantes = [
        ("Laura Gómez", "20232001", "laura@tandem.edu", ["Cálculo I", "Programación"]),
        ("Sebastián Rincón", "20232002", "sebastian@tandem.edu", ["Física I", "Álgebra Lineal"]),
        ("Mariana León", "20232003", "mariana@tandem.edu", ["Bases de Datos", "Estadística"]),
    ]
    ids_est = []
    for nombre, cod, correo, mats in estudiantes:
        eid = usuario(nombre, cod, correo, "estudiante", "Ingeniería de Sistemas")
        ids_est.append(eid)
        for m in mats:
            db.execute("INSERT INTO inscripciones VALUES (?, ?)", (eid, materias[m]))

    # Solicitudes de ejemplo en distintos estados
    hoy = date.today()
    f = lambda d: (hoy + timedelta(days=d)).isoformat()
    sol = lambda est, mat, tema, dias, estado, mon=None: db.execute(
        "INSERT INTO solicitudes (estudiante_id, materia_id, tema, fecha_preferida, estado, monitor_id) VALUES (?,?,?,?,?,?)",
        (est, materias[mat], tema, f(dias), estado, mon)).lastrowid

    sol(ids_est[0], "Cálculo I", "Derivadas parciales", 3, "pendiente")
    sol(ids_est[1], "Física I", "Cinemática en dos dimensiones", 4, "pendiente")
    s3 = sol(ids_est[0], "Programación", "Ciclos y listas en Python", 1, "asignada", ids_mon[1])
    s4 = sol(ids_est[2], "Estadística", "Distribución normal", -3, "atendida", ids_mon[3])
    db.execute("INSERT INTO sesiones (solicitud_id, asistio, temas_vistos) VALUES (?, 1, ?)", (s4, "Z-score y tablas de la normal"))
    sol(ids_est[1], "Álgebra Lineal", "Valores propios", -6, "cancelada")

    # Más estudiantes y solicitudes para que la paginación y los filtros se vean con datos reales.
    for nombre, cod in [("Diana Ríos", "20232004"), ("Camilo Torres", "20232005"), ("Natalia Pardo", "20232006"), ("Esteban Cruz", "20232007")]:
        ids_est.append(usuario(nombre, cod, nombre.split()[0].lower() + "@tandem.edu", "estudiante", "Ingeniería de Sistemas"))
    atiende = {  # materia -> monitor que la atiende
        "Cálculo I": ids_mon[0], "Álgebra Lineal": ids_mon[0], "Programación": ids_mon[1], "Bases de Datos": ids_mon[1],
        "Física I": ids_mon[2], "Estadística": ids_mon[3],
    }
    temas = {
        "Cálculo I": ["Límites", "Regla de la cadena", "Integrales por partes", "Optimización"],
        "Álgebra Lineal": ["Matrices inversas", "Determinantes", "Espacios vectoriales"],
        "Programación": ["Funciones en Python", "Diccionarios", "Recursión", "Archivos"],
        "Bases de Datos": ["Normalización", "Consultas JOIN", "Llaves foráneas"],
        "Física I": ["Leyes de Newton", "Energía cinética", "Movimiento circular"],
        "Estadística": ["Media y varianza", "Regresión lineal", "Probabilidad condicional"],
    }
    estados = ["atendida", "atendida", "asignada", "pendiente", "cancelada", "atendida", "pendiente"]
    n = 0
    for materia, lista_temas in temas.items():
        for tema in lista_temas:
            estado = estados[n % len(estados)]
            est = ids_est[n % len(ids_est)]
            mon = atiende[materia] if estado in ("asignada", "atendida") else None
            sid = sol(est, materia, tema, (n % 9) - 6, estado, mon)
            if estado == "atendida":
                db.execute("INSERT INTO sesiones (solicitud_id, asistio, temas_vistos) VALUES (?, ?, ?)",
                           (sid, 0 if n % 5 == 4 else 1, "Repaso de " + tema.lower() + " con ejercicios"))
            n += 1

    db.commit()
    db.close()
    print("Base de datos creada en", Config.DATABASE)
    print("Usuarios de ejemplo (clave para todos:", CLAVE_DEMO + ")")
    print("  bienestar@tandem.edu | docente.calculo@tandem.edu | camila@tandem.edu | laura@tandem.edu")


if __name__ == "__main__":
    main()
