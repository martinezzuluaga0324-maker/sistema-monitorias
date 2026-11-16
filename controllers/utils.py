"""Herramientas compartidas por los controladores: sesión, permisos por rol, CSRF y validaciones."""
import re
import secrets
from datetime import date
from functools import wraps
from flask import session, redirect, url_for, flash, abort, request, g

import models.usuario as usuarios

# Cada rol tiene su "casa" (la página a la que llega después de ingresar).
INICIO_POR_ROL = {
    "estudiante": "estudiante.panel",
    "monitor": "monitor.panel",
    "docente": "docente.panel",
    "bienestar": "bienestar.panel",
}


# ---------- Sesión y permisos ----------
def cargar_usuario():
    """Se ejecuta antes de cada petición: deja el usuario actual en g.usuario (o None)."""
    uid = session.get("usuario_id")
    g.usuario = usuarios.por_id(uid) if uid else None


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*a, **kw):
        if g.usuario is None:
            flash("Inicia sesión para continuar.", "aviso")
            return redirect(url_for("auth.login", siguiente=request.path))
        return vista(*a, **kw)
    return envoltura


def rol_requerido(*roles):
    """Solo deja pasar a los roles indicados; a los demás les responde 403."""
    def decorador(vista):
        @wraps(vista)
        @login_requerido
        def envoltura(*a, **kw):
            if g.usuario["rol"] not in roles:
                abort(403)
            return vista(*a, **kw)
        return envoltura
    return decorador


# ---------- CSRF: evita que otra web envíe formularios en nombre del usuario ----------
def token_csrf():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


def verificar_csrf():
    """Se ejecuta antes de cada POST: el token del formulario debe coincidir con el de la sesión."""
    if request.method == "POST":
        enviado = request.form.get("csrf") or request.headers.get("X-CSRF")
        if not enviado or not secrets.compare_digest(enviado, session.get("csrf", "")):
            abort(400)


# ---------- Validaciones del lado del servidor ----------
RE_CORREO = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validar_usuario(f, editando=False):
    """Revisa los datos de registro/edición de usuario. Devuelve un dict {campo: mensaje}."""
    e = {}
    if len(f.get("nombre", "").split()) < 2:
        e["nombre"] = "Escribe nombre y apellido."
    if not RE_CORREO.match(f.get("correo", "").strip()):
        e["correo"] = "Escribe un correo válido."
    codigo = f.get("codigo", "").strip()
    if f.get("rol", "estudiante") in ("estudiante", "monitor") and not re.fullmatch(r"\d{6,10}", codigo):
        e["codigo"] = "El código tiene entre 6 y 10 dígitos."
    clave = f.get("clave", "")
    if (not editando or clave) and len(clave) < 8:
        e["clave"] = "La contraseña debe tener mínimo 8 caracteres."
    return e


def validar_solicitud(f):
    e = {}
    if not f.get("materia_id", "").isdigit():
        e["materia_id"] = "Selecciona la materia."
    if len(f.get("tema", "").strip()) < 4:
        e["tema"] = "Describe el tema (mínimo 4 letras)."
    fecha = f.get("fecha", "")
    try:
        if date.fromisoformat(fecha) < date.today():
            e["fecha"] = "La fecha no puede ser anterior a hoy."
    except ValueError:
        e["fecha"] = "Elige una fecha válida."
    return e


def validar_franja(f):
    from models.disponibilidad import DIAS
    e = {}
    if f.get("dia") not in DIAS:
        e["dia"] = "Selecciona el día."
    ini, fin = f.get("hora_inicio", ""), f.get("hora_fin", "")
    if not re.fullmatch(r"\d\d:\d\d", ini):
        e["hora_inicio"] = "Hora de inicio inválida."
    if not re.fullmatch(r"\d\d:\d\d", fin):
        e["hora_fin"] = "Hora de fin inválida."
    elif "hora_inicio" not in e and fin <= ini:
        e["hora_fin"] = "La hora de fin debe ser después de la de inicio."
    return e


POR_PAGINA = 10


def paginar():
    """Lee ?pagina=N de la dirección y calcula el OFFSET. Devuelve (pagina, offset)."""
    pagina = max(request.args.get("pagina", 1, type=int), 1)
    return pagina, (pagina - 1) * POR_PAGINA


def info_paginas(pagina, total):
    """Datos que necesita la plantilla para dibujar los botones de paginación."""
    paginas = max((total + POR_PAGINA - 1) // POR_PAGINA, 1)
    return {"pagina": min(pagina, paginas), "paginas": paginas, "total": total, "por_pagina": POR_PAGINA}


def ids_de(lista):
    """Convierte los valores de un select/checkbox múltiple en enteros."""
    return [int(x) for x in lista if str(x).isdigit()]


def paginado(consulta, **filtros):
    """Ejecuta una consulta de un modelo para la página pedida. Devuelve (filas, info de paginación)."""
    pagina, offset = paginar()
    filas, total = consulta(limite=POR_PAGINA, offset=offset, **filtros)
    info = info_paginas(pagina, total)
    if info["pagina"] != pagina:  # pidieron una página que no existe: se muestra la última
        filas, total = consulta(limite=POR_PAGINA, offset=(info["pagina"] - 1) * POR_PAGINA, **filtros)
    return filas, info
