"""Panel del estudiante: solicitar, ver, editar y cancelar monitorías (HU-2, HU-3, HU-4)."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort

import models.solicitud as solicitudes
import models.materia as materias
import models.disponibilidad as disponibilidad
from controllers.utils import rol_requerido, validar_solicitud

bp = Blueprint("estudiante", __name__, url_prefix="/estudiante")


def _propia(solicitud_id):
    """Trae la solicitud solo si es del estudiante que la pide; si no, 404."""
    s = solicitudes.por_id(solicitud_id)
    if s is None or s["estudiante_id"] != g.usuario["id"]:
        abort(404)
    return s


@bp.route("/")
@rol_requerido("estudiante")
def panel():
    return render_template("estudiante/panel.html", solicitudes=solicitudes.de_estudiante(g.usuario["id"]))


@bp.route("/monitores")
@rol_requerido("estudiante")
def monitores():
    """Monitores de una materia con sus días y horas (HU-3)."""
    materia_id = request.args.get("materia", type=int)
    return render_template(
        "estudiante/monitores.html",
        monitores=disponibilidad.monitores_con_agenda(materia_id, request.args.get("q", "").strip()),
        materias=materias.listar(), materia_id=materia_id,
    )


@bp.route("/solicitudes/nueva", methods=["GET", "POST"])
@rol_requerido("estudiante")
def nueva():
    errores = {}
    if request.method == "POST":
        errores = validar_solicitud(request.form)
        if "materia_id" not in errores and not materias.por_id(int(request.form["materia_id"])):
            errores["materia_id"] = "Esa materia no existe."
        if not errores:
            solicitudes.crear(
                g.usuario["id"], int(request.form["materia_id"]), request.form["tema"].strip(),
                request.form["fecha"], request.form.get("notas", "").strip(),
            )
            flash("Solicitud enviada. Quedó en estado pendiente.", "ok")
            return redirect(url_for("estudiante.panel"))
    return render_template(
        "estudiante/solicitud_form.html", errores=errores, datos=request.form,
        materias=materias.listar(), solicitud=None,
        materia_sugerida=request.args.get("materia", type=int),
    )


@bp.route("/solicitudes/<int:solicitud_id>/editar", methods=["GET", "POST"])
@rol_requerido("estudiante")
def editar(solicitud_id):
    s = _propia(solicitud_id)
    if s["estado"] != "pendiente":
        flash("Solo puedes editar solicitudes pendientes.", "error")
        return redirect(url_for("estudiante.panel"))
    errores = {}
    if request.method == "POST":
        errores = validar_solicitud(request.form)
        if "materia_id" not in errores and not materias.por_id(int(request.form["materia_id"])):
            errores["materia_id"] = "Esa materia no existe."
        if not errores:
            solicitudes.actualizar(
                solicitud_id, int(request.form["materia_id"]), request.form["tema"].strip(),
                request.form["fecha"], request.form.get("notas", "").strip(),
            )
            flash("Solicitud actualizada.", "ok")
            return redirect(url_for("estudiante.panel"))
    datos = request.form if request.method == "POST" else {
        "materia_id": s["materia_id"], "tema": s["tema"], "fecha": s["fecha_preferida"], "notas": s["notas"] or "",
    }
    return render_template("estudiante/solicitud_form.html", errores=errores, datos=datos, materias=materias.listar(), solicitud=s)


@bp.route("/solicitudes/<int:solicitud_id>/cancelar", methods=["POST"])
@rol_requerido("estudiante")
def cancelar(solicitud_id):
    s = _propia(solicitud_id)
    if s["estado"] in ("pendiente", "asignada"):
        solicitudes.cancelar(solicitud_id)
        flash("Solicitud cancelada.", "ok")
    else:
        flash("Esa solicitud ya no se puede cancelar.", "error")
    return redirect(url_for("estudiante.panel"))


@bp.route("/solicitudes/<int:solicitud_id>/eliminar", methods=["POST"])
@rol_requerido("estudiante")
def eliminar(solicitud_id):
    s = _propia(solicitud_id)
    if s["estado"] in ("cancelada", "pendiente"):
        solicitudes.eliminar(solicitud_id)
        flash("Solicitud eliminada.", "ok")
    else:
        flash("Solo puedes eliminar solicitudes pendientes o canceladas.", "error")
    return redirect(url_for("estudiante.panel"))
