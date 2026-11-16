"""Modelo Solicitud: pedidos de monitoría (CRUD) y sesiones registradas por el monitor."""
from database import get_db

# Consulta base: une cada solicitud con los nombres de materia, estudiante y monitor.
BASE = """
SELECT s.*, ma.nombre AS materia, e.nombre AS estudiante, e.codigo AS codigo,
       mo.nombre AS monitor, ses.asistio, ses.temas_vistos
FROM solicitudes s
JOIN materias ma ON ma.id = s.materia_id
JOIN usuarios e ON e.id = s.estudiante_id
LEFT JOIN usuarios mo ON mo.id = s.monitor_id
LEFT JOIN sesiones ses ON ses.solicitud_id = s.id
"""


def crear(estudiante_id, materia_id, tema, fecha, notas, remitida_por=None):
    db = get_db()
    cur = db.execute(
        """INSERT INTO solicitudes (estudiante_id, materia_id, tema, fecha_preferida, notas, remitida_por)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (estudiante_id, materia_id, tema, fecha, notas, remitida_por),
    )
    db.commit()
    return cur.lastrowid


def por_id(solicitud_id):
    return get_db().execute(BASE + " WHERE s.id = ?", (solicitud_id,)).fetchone()


def de_estudiante(estudiante_id):
    return get_db().execute(BASE + " WHERE s.estudiante_id = ? ORDER BY s.creado_en DESC", (estudiante_id,)).fetchall()


def actualizar(solicitud_id, materia_id, tema, fecha, notas):
    db = get_db()
    db.execute(
        "UPDATE solicitudes SET materia_id=?, tema=?, fecha_preferida=?, notas=? WHERE id=?",
        (materia_id, tema, fecha, notas, solicitud_id),
    )
    db.commit()


def cancelar(solicitud_id):
    db = get_db()
    db.execute("UPDATE solicitudes SET estado='cancelada' WHERE id = ?", (solicitud_id,))
    db.commit()


def eliminar(solicitud_id):
    db = get_db()
    db.execute("DELETE FROM solicitudes WHERE id = ?", (solicitud_id,))
    db.commit()


# ----- Bienestar -----
def pendientes():
    return get_db().execute(BASE + " WHERE s.estado = 'pendiente' ORDER BY s.fecha_preferida").fetchall()


def asignar(solicitud_id, monitor_id):
    db = get_db()
    db.execute("UPDATE solicitudes SET monitor_id=?, estado='asignada' WHERE id=?", (monitor_id, solicitud_id))
    db.commit()


def monitores_para_materia(materia_id):
    """Monitores que atienden esa materia (para elegir al asignar)."""
    return get_db().execute(
        """SELECT u.id, u.nombre FROM usuarios u
           JOIN monitor_materias mm ON mm.monitor_id = u.id
           WHERE mm.materia_id = ? ORDER BY u.nombre""",
        (materia_id,),
    ).fetchall()


def reporte(materia_id=None, monitor_id=None, estado=None, texto=""):
    """Reporte filtrable (HU-10) y búsqueda dinámica."""
    sql, params = BASE + " WHERE 1=1", []
    if materia_id:
        sql += " AND s.materia_id = ?"; params.append(materia_id)
    if monitor_id:
        sql += " AND s.monitor_id = ?"; params.append(monitor_id)
    if estado:
        sql += " AND s.estado = ?"; params.append(estado)
    if texto:
        sql += " AND (s.tema LIKE ? OR e.nombre LIKE ?)"; params += [f"%{texto}%"] * 2
    return get_db().execute(sql + " ORDER BY s.creado_en DESC", params).fetchall()


def resumen_por_materia():
    return get_db().execute(
        """SELECT ma.nombre AS materia, COUNT(s.id) AS total,
                  SUM(s.estado = 'atendida') AS atendidas, SUM(s.estado = 'pendiente') AS pendientes
           FROM materias ma LEFT JOIN solicitudes s ON s.materia_id = ma.id
           GROUP BY ma.id ORDER BY total DESC, ma.nombre"""
    ).fetchall()


# ----- Monitor -----
def de_monitor(monitor_id):
    return get_db().execute(BASE + " WHERE s.monitor_id = ? ORDER BY s.fecha_preferida", (monitor_id,)).fetchall()


def registrar_sesion(solicitud_id, asistio, temas):
    """Guarda (o corrige) la asistencia y marca la solicitud como atendida (HU-6)."""
    db = get_db()
    existe = db.execute("SELECT 1 FROM sesiones WHERE solicitud_id = ?", (solicitud_id,)).fetchone()
    if existe:
        db.execute("UPDATE sesiones SET asistio=?, temas_vistos=? WHERE solicitud_id=?", (asistio, temas, solicitud_id))
    else:
        db.execute("INSERT INTO sesiones (solicitud_id, asistio, temas_vistos) VALUES (?, ?, ?)", (solicitud_id, asistio, temas))
    db.execute("UPDATE solicitudes SET estado='atendida' WHERE id=?", (solicitud_id,))
    db.commit()


# ----- Docente -----
def historial_docente(docente_id, materia_id=None, texto=""):
    """Solicitudes de los estudiantes de las materias de ese docente (HU-8)."""
    sql = BASE + " WHERE ma.docente_id = ?"
    params = [docente_id]
    if materia_id:
        sql += " AND s.materia_id = ?"; params.append(materia_id)
    if texto:
        sql += " AND (e.nombre LIKE ? OR s.tema LIKE ?)"; params += [f"%{texto}%"] * 2
    return get_db().execute(sql + " ORDER BY s.creado_en DESC", params).fetchall()
