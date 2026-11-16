"""Modelo Materia, inscripciones de estudiantes y materias que atiende cada monitor."""
from database import get_db


def listar():
    return get_db().execute(
        """SELECT m.*, u.nombre AS docente
           FROM materias m LEFT JOIN usuarios u ON u.id = m.docente_id
           ORDER BY m.nombre"""
    ).fetchall()


def por_id(materia_id):
    return get_db().execute("SELECT * FROM materias WHERE id = ?", (materia_id,)).fetchone()


def por_nombre(nombre):
    return get_db().execute("SELECT * FROM materias WHERE nombre = ?", (nombre,)).fetchone()


def crear(nombre, docente_id):
    db = get_db()
    db.execute("INSERT INTO materias (nombre, docente_id) VALUES (?, ?)", (nombre, docente_id or None))
    db.commit()


def actualizar(materia_id, nombre, docente_id):
    db = get_db()
    db.execute("UPDATE materias SET nombre=?, docente_id=? WHERE id=?", (nombre, docente_id or None, materia_id))
    db.commit()


def eliminar(materia_id):
    db = get_db()
    db.execute("DELETE FROM materias WHERE id = ?", (materia_id,))
    db.commit()


def en_uso(materia_id):
    """True si hay solicitudes de esta materia (no se puede borrar)."""
    return get_db().execute("SELECT 1 FROM solicitudes WHERE materia_id = ? LIMIT 1", (materia_id,)).fetchone() is not None


# ----- Inscripciones (qué estudiante cursa qué materia) -----
def fijar_inscripciones(estudiante_id, ids_materias):
    """Reemplaza las materias inscritas del estudiante por la lista recibida."""
    db = get_db()
    db.execute("DELETE FROM inscripciones WHERE estudiante_id = ?", (estudiante_id,))
    for mid in ids_materias:
        db.execute("INSERT OR IGNORE INTO inscripciones VALUES (?, ?)", (estudiante_id, mid))
    db.commit()


def inscritas(estudiante_id):
    return [r["materia_id"] for r in get_db().execute(
        "SELECT materia_id FROM inscripciones WHERE estudiante_id = ?", (estudiante_id,)).fetchall()]


def estudiantes_de_docente(docente_id):
    """Estudiantes inscritos en las materias de un docente (HU-7)."""
    return get_db().execute(
        """SELECT u.id, u.nombre, u.codigo, m.id AS materia_id, m.nombre AS materia
           FROM materias m
           JOIN inscripciones i ON i.materia_id = m.id
           JOIN usuarios u ON u.id = i.estudiante_id
           WHERE m.docente_id = ?
           ORDER BY m.nombre, u.nombre""",
        (docente_id,),
    ).fetchall()


def de_docente(docente_id):
    return get_db().execute("SELECT * FROM materias WHERE docente_id = ? ORDER BY nombre", (docente_id,)).fetchall()


# ----- Materias de un monitor -----
def fijar_materias_monitor(monitor_id, ids_materias):
    """Reemplaza las materias que atiende el monitor por la lista recibida."""
    db = get_db()
    db.execute("DELETE FROM monitor_materias WHERE monitor_id = ?", (monitor_id,))
    for mid in ids_materias:
        db.execute("INSERT OR IGNORE INTO monitor_materias VALUES (?, ?)", (monitor_id, mid))
    db.commit()


def de_monitor(monitor_id):
    return get_db().execute(
        "SELECT m.* FROM materias m JOIN monitor_materias mm ON mm.materia_id = m.id WHERE mm.monitor_id = ? ORDER BY m.nombre",
        (monitor_id,),
    ).fetchall()
