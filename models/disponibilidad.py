"""Modelo Disponibilidad: franjas libres de cada monitor (CRUD completo) y búsqueda de monitores."""
from database import get_db

DIAS = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado")


def crear(monitor_id, dia, inicio, fin):
    db = get_db()
    db.execute(
        "INSERT INTO disponibilidades (monitor_id, dia, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)",
        (monitor_id, dia, inicio, fin),
    )
    db.commit()


def de_monitor(monitor_id):
    return get_db().execute(
        """SELECT * FROM disponibilidades WHERE monitor_id = ?
           ORDER BY CASE dia WHEN 'Lunes' THEN 1 WHEN 'Martes' THEN 2 WHEN 'Miércoles' THEN 3
                             WHEN 'Jueves' THEN 4 WHEN 'Viernes' THEN 5 ELSE 6 END, hora_inicio""",
        (monitor_id,),
    ).fetchall()


def por_id(disp_id):
    return get_db().execute("SELECT * FROM disponibilidades WHERE id = ?", (disp_id,)).fetchone()


def actualizar(disp_id, dia, inicio, fin):
    db = get_db()
    db.execute("UPDATE disponibilidades SET dia=?, hora_inicio=?, hora_fin=? WHERE id=?", (dia, inicio, fin, disp_id))
    db.commit()


def eliminar(disp_id):
    db = get_db()
    db.execute("DELETE FROM disponibilidades WHERE id = ?", (disp_id,))
    db.commit()


def monitores_con_agenda(materia_id=None, texto=""):
    """Monitores con sus materias y franjas (HU-3). Filtra por materia y por texto (nombre)."""
    db = get_db()
    sql = """SELECT DISTINCT u.id, u.nombre, u.programa FROM usuarios u
             LEFT JOIN monitor_materias mm ON mm.monitor_id = u.id
             WHERE u.rol = 'monitor'"""
    params = []
    if materia_id:
        sql += " AND mm.materia_id = ?"
        params.append(materia_id)
    if texto:
        sql += " AND u.nombre LIKE ?"
        params.append(f"%{texto}%")
    monitores = []
    for m in db.execute(sql + " ORDER BY u.nombre", params).fetchall():
        materias = db.execute(
            "SELECT ma.nombre FROM materias ma JOIN monitor_materias mm ON mm.materia_id = ma.id WHERE mm.monitor_id = ?",
            (m["id"],),
        ).fetchall()
        monitores.append({
            "id": m["id"],
            "nombre": m["nombre"],
            "programa": m["programa"],
            "materias": [x["nombre"] for x in materias],
            "franjas": [f"{d['dia']} {d['hora_inicio']} – {d['hora_fin']}" for d in de_monitor(m["id"])],
        })
    return monitores
