"""Panel del monitor: su disponibilidad (CRUD) y el registro de sesiones (HU-5, HU-6)."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort

import models.disponibilidad as disponibilidad
import models.solicitud as solicitudes
import models.materia as materias
from controllers.utils import rol_requerido, validar_franja

bp = Blueprint("monitor", __name__, url_prefix="/monitor")


@bp.route("/")
@rol_requerido("monitor")
def panel():
    return render_template(
        "monitor/panel.html",
        franjas=disponibilidad.de_monitor(g.usuario["id"]),
        asignadas=solicitudes.de_monitor(g.usuario["id"]),
        materias=materias.de_monitor(g.usuario["id"]),
    )


@bp.route("/disponibilidad/nueva", methods=["GET", "POST"])
@rol_requerido("monitor")
def nueva_franja():
    errores = {}
    if request.method == "POST":
        errores = validar_franja(request.form)
        if not errores:
            disponibilidad.crear(g.usuario["id"], request.form["dia"], request.form["hora_inicio"], request.form["hora_fin"])
            flash("Franja agregada.", "ok")
            return redirect(url_for("monitor.panel"))
    return render_template("monitor/franja_form.html", errores=errores, datos=request.form, dias=disponibilidad.DIAS, franja=None)


@bp.route("/disponibilidad/<int:disp_id>/editar", methods=["GET", "POST"])
@rol_requerido("monitor")
def editar_franja(disp_id):
    f = disponibilidad.por_id(disp_id)
    if f is None or f["monitor_id"] != g.usuario["id"]:
        abort(404)
    errores = {}
    if request.method == "POST":
        errores = validar_franja(request.form)
        if not errores:
            disponibilidad.actualizar(disp_id, request.form["dia"], request.form["hora_inicio"], request.form["hora_fin"])
            flash("Franja actualizada.", "ok")
            return redirect(url_for("monitor.panel"))
    datos = request.form if request.method == "POST" else {"dia": f["dia"], "hora_inicio": f["hora_inicio"], "hora_fin": f["hora_fin"]}
    return render_template("monitor/franja_form.html", errores=errores, datos=datos, dias=disponibilidad.DIAS, franja=f)


@bp.route("/disponibilidad/<int:disp_id>/eliminar", methods=["POST"])
@rol_requerido("monitor")
def eliminar_franja(disp_id):
    f = disponibilidad.por_id(disp_id)
    if f is None or f["monitor_id"] != g.usuario["id"]:
        abort(404)
    disponibilidad.eliminar(disp_id)
    flash("Franja eliminada.", "ok")
    return redirect(url_for("monitor.panel"))


@bp.route("/sesion/<int:solicitud_id>", methods=["GET", "POST"])
@rol_requerido("monitor")
def sesion(solicitud_id):
    """Registra si el estudiante asistió y qué temas se vieron."""
    s = solicitudes.por_id(solicitud_id)
    if s is None or s["monitor_id"] != g.usuario["id"] or s["estado"] == "cancelada":
        abort(404)
    errores = {}
    if request.method == "POST":
        asistio = 1 if request.form.get("asistio") == "1" else 0
        temas = request.form.get("temas_vistos", "").strip()
        if asistio and len(temas) < 4:
            errores["temas_vistos"] = "Si asistió, anota los temas vistos."
        if not errores:
            solicitudes.registrar_sesion(solicitud_id, asistio, temas)
            flash("Sesión registrada.", "ok")
            return redirect(url_for("monitor.panel"))
    datos = request.form if request.method == "POST" else {
        "asistio": "0" if s["asistio"] == 0 else "1", "temas_vistos": s["temas_vistos"] or "",
    }
    return render_template("monitor/sesion_form.html", s=s, errores=errores, datos=datos)
