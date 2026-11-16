"""Modelo Usuario: todo lo que se hace con la tabla `usuarios`."""
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

ROLES = ("estudiante", "monitor", "docente", "bienestar")


def crear(nombre, codigo, correo, clave, rol, programa):
    db = get_db()
    cur = db.execute(
        "INSERT INTO usuarios (nombre, codigo, correo, clave_hash, rol, programa) VALUES (?, ?, ?, ?, ?, ?)",
        (nombre, codigo or None, correo.lower(), generate_password_hash(clave), rol, programa),
    )
    db.commit()
    return cur.lastrowid


def por_id(usuario_id):
    return get_db().execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()


def por_correo(correo):
    return get_db().execute("SELECT * FROM usuarios WHERE correo = ?", (correo.lower(),)).fetchone()


def por_codigo(codigo):
    return get_db().execute("SELECT * FROM usuarios WHERE codigo = ?", (codigo,)).fetchone()


def verificar(correo, clave):
    """Devuelve el usuario si correo y contraseña son correctos; si no, None."""
    u = por_correo(correo)
    if u and check_password_hash(u["clave_hash"], clave):
        return u
    return None


def listar(rol=None, texto="", limite=10, offset=0):
    """Usuarios filtrados y paginados. Devuelve (filas de la página, total de filas)."""
    donde, params = " WHERE 1=1", []
    if rol:
        donde += " AND rol = ?"
        params.append(rol)
    if texto:
        donde += " AND (nombre LIKE ? OR correo LIKE ? OR codigo LIKE ?)"
        params += [f"%{texto}%"] * 3
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM usuarios" + donde, params).fetchone()[0]
    filas = db.execute("SELECT * FROM usuarios" + donde + " ORDER BY rol, nombre LIMIT ? OFFSET ?", params + [limite, offset]).fetchall()
    return filas, total


def actualizar(usuario_id, nombre, codigo, correo, rol, programa, clave=None):
    db = get_db()
    db.execute(
        "UPDATE usuarios SET nombre=?, codigo=?, correo=?, rol=?, programa=? WHERE id=?",
        (nombre, codigo or None, correo.lower(), rol, programa, usuario_id),
    )
    if clave:  # solo cambia la contraseña si escribieron una nueva
        db.execute("UPDATE usuarios SET clave_hash=? WHERE id=?", (generate_password_hash(clave), usuario_id))
    db.commit()


def eliminar(usuario_id):
    db = get_db()
    db.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    db.commit()


def por_rol(rol):
    return get_db().execute("SELECT id, nombre FROM usuarios WHERE rol = ? ORDER BY nombre", (rol,)).fetchall()
