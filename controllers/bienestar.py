"""Panel de Bienestar Institucional: asignar monitores, reportes y gestión (HU-9, HU-10 + CRUD)."""
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort, jsonify

import models.usuario as usuarios
import models.materia as materias
import models.solicitud as solicitudes
from controllers.utils import rol_requerido, validar_usuario, ids_de, paginado

bp = Blueprint("bienestar", __name__, url_prefix="/bienestar")


# ---------- Asignación (HU-9) ----------
@bp.route("/")
@rol_requerido("bienestar")
def panel():
    pend = solicitudes.pendientes()
    # Para cada solicitud pendiente, los monitores que atienden esa materia.
    opciones = {s["id"]: solicitudes.monitores_para_materia(s["materia_id"]) for s in pend}
    return render_template("bienestar/panel.html", pendientes=pend, opciones=opciones, resumen=solicitudes.resumen_por_materia())


@bp.route("/asignar/<int:solicitud_id>", methods=["POST"])
@rol_requerido("bienestar")
def asignar(solicitud_id):
    s = solicitudes.por_id(solicitud_id)
    monitor_id = request.form.get("monitor_id", type=int)
    if s is None or s["estado"] != "pendiente":
        abort(404)
    if monitor_id not in [m["id"] for m in solicitudes.monitores_para_materia(s["materia_id"])]:
        flash("Elige un monitor que atienda esa materia.", "error")
    else:
        solicitudes.asignar(solicitud_id, monitor_id)
        flash("Monitor asignado.", "ok")
    return redirect(url_for("bienestar.panel"))


# ---------- Reportes con filtros y búsqueda dinámica (HU-10) ----------
def _filtros():
    return dict(
        materia_id=request.args.get("materia", type=int),
        monitor_id=request.args.get("monitor", type=int),
        estado=request.args.get("estado") or None,
        texto=request.args.get("q", "").strip(),
    )


@bp.route("/reportes")
@rol_requerido("bienestar")
def reportes():
    f = _filtros()
    filas, pag = paginado(solicitudes.reporte, **f)
    return render_template(
        "bienestar/reportes.html", filas=filas, pag=pag, materias=materias.listar(),
        monitores=usuarios.por_rol("monitor"), f=f,
    )


@bp.route("/api/reportes")
@rol_requerido("bienestar")
def api_reportes():
    """Misma consulta en JSON: la página la pide con fetch() mientras se escribe en el buscador."""
    filas, pag = paginado(solicitudes.reporte, **_filtros())
    return jsonify({
        "pagina": pag["pagina"], "paginas": pag["paginas"], "total": pag["total"],
        "filas": [
            {"id": s["id"], "estudiante": s["estudiante"], "materia": s["materia"], "tema": s["tema"],
             "fecha": s["fecha_preferida"], "monitor": s["monitor"] or "—", "estado": s["estado"],
             "asistio": None if s["asistio"] is None else bool(s["asistio"])}
            for s in filas
        ],
    })


# ---------- CRUD de usuarios ----------
@bp.route("/usuarios")
@rol_requerido("bienestar")
def usuarios_lista():
    rol = request.args.get("rol") or None
    filas, pag = paginado(usuarios.listar, rol=rol, texto=request.args.get("q", "").strip())
    return render_template("bienestar/usuarios.html", filas=filas, pag=pag, rol=rol, roles=usuarios.ROLES)


@bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@rol_requerido("bienestar")
def usuario_nuevo():
    return _usuario_form(None)


@bp.route("/usuarios/<int:uid>/editar", methods=["GET", "POST"])
@rol_requerido("bienestar")
def usuario_editar(uid):
    u = usuarios.por_id(uid)
    if u is None:
        abort(404)
    return _usuario_form(u)


def _usuario_form(u):
    errores = {}
    if request.method == "POST":
        errores = validar_usuario(request.form, editando=u is not None)
        if request.form.get("rol") not in usuarios.ROLES:
            errores["rol"] = "Selecciona el rol."
        otro = usuarios.por_correo(request.form.get("correo", ""))
        if "correo" not in errores and otro and (u is None or otro["id"] != u["id"]):
            errores["correo"] = "Ese correo ya está registrado."
        cod = request.form.get("codigo", "").strip()
        otro = usuarios.por_codigo(cod) if cod else None
        if "codigo" not in errores and otro and (u is None or otro["id"] != u["id"]):
            errores["codigo"] = "Ese código ya está registrado."
        if not errores:
            rol = request.form["rol"]
            campos = (request.form["nombre"].strip(), cod, request.form["correo"].strip(), rol, request.form.get("programa", "").strip())
            if u is None:
                uid = usuarios.crear(campos[0], campos[1], campos[2], request.form["clave"], rol, campos[4])
            else:
                uid = u["id"]
                usuarios.actualizar(uid, *campos, clave=request.form.get("clave") or None)
            ids = ids_de(request.form.getlist("materias"))
            if rol == "monitor":
                materias.fijar_materias_monitor(uid, ids)
            elif rol == "estudiante":
                materias.fijar_inscripciones(uid, ids)
            flash("Usuario guardado.", "ok")
            return redirect(url_for("bienestar.usuarios_lista"))
    if request.method == "POST":
        datos, marcadas = request.form, ids_de(request.form.getlist("materias"))
    elif u:
        datos = dict(u)
        marcadas = [m["id"] for m in materias.de_monitor(u["id"])] if u["rol"] == "monitor" else materias.inscritas(u["id"])
    else:
        datos, marcadas = {}, []
    return render_template("bienestar/usuario_form.html", u=u, errores=errores, datos=datos, roles=usuarios.ROLES, materias=materias.listar(), marcadas=marcadas)


@bp.route("/usuarios/<int:uid>/eliminar", methods=["POST"])
@rol_requerido("bienestar")
def usuario_eliminar(uid):
    if uid == g.usuario["id"]:
        flash("No puedes eliminar tu propia cuenta.", "error")
    else:
        usuarios.eliminar(uid)
        flash("Usuario eliminado.", "ok")
    return redirect(url_for("bienestar.usuarios_lista"))


# ---------- CRUD de materias ----------
@bp.route("/materias")
@rol_requerido("bienestar")
def materias_lista():
    return render_template("bienestar/materias.html", filas=materias.listar())


@bp.route("/materias/nueva", methods=["GET", "POST"])
@rol_requerido("bienestar")
def materia_nueva():
    return _materia_form(None)


@bp.route("/materias/<int:mid>/editar", methods=["GET", "POST"])
@rol_requerido("bienestar")
def materia_editar(mid):
    m = materias.por_id(mid)
    if m is None:
        abort(404)
    return _materia_form(m)


def _materia_form(m):
    errores = {}
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        docente_id = request.form.get("docente_id", type=int)
        if len(nombre) < 3:
            errores["nombre"] = "El nombre debe tener mínimo 3 letras."
        existe = materias.por_nombre(nombre)
        if not errores and existe and (m is None or existe["id"] != m["id"]):
            errores["nombre"] = "Ya existe una materia con ese nombre."
        if not errores:
            try:
                materias.actualizar(m["id"], nombre, docente_id) if m else materias.crear(nombre, docente_id)
            except sqlite3.IntegrityError:
                errores["nombre"] = "No se pudo guardar: revisa los datos."
            else:
                flash("Materia guardada.", "ok")
                return redirect(url_for("bienestar.materias_lista"))
    datos = request.form if request.method == "POST" else (dict(m) if m else {})
    return render_template("bienestar/materia_form.html", m=m, errores=errores, datos=datos, docentes=usuarios.por_rol("docente"))


@bp.route("/materias/<int:mid>/eliminar", methods=["POST"])
@rol_requerido("bienestar")
def materia_eliminar(mid):
    if materias.en_uso(mid):
        flash("No se puede eliminar: ya tiene solicitudes registradas.", "error")
    else:
        materias.eliminar(mid)
        flash("Materia eliminada.", "ok")
    return redirect(url_for("bienestar.materias_lista"))
