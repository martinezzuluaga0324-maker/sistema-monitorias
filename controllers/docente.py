"""Panel del docente: remitir estudiantes y ver su historial (HU-7, HU-8)."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from datetime import date

import models.materia as materias
import models.solicitud as solicitudes
from controllers.utils import rol_requerido, paginado

bp = Blueprint("docente", __name__, url_prefix="/docente")


@bp.route("/")
@rol_requerido("docente")
def panel():
    return render_template("docente/panel.html", estudiantes=materias.estudiantes_de_docente(g.usuario["id"]), hoy=date.today().isoformat())


@bp.route("/remitir", methods=["POST"])
@rol_requerido("docente")
def remitir():
    """Crea una solicitud a nombre del estudiante, marcada como remitida por este docente."""
    est_id, mat_id = request.form.get("estudiante_id", type=int), request.form.get("materia_id", type=int)
    tema = request.form.get("tema", "").strip()
    # Seguridad: solo se puede remitir a estudiantes inscritos en una materia propia.
    permitido = any(e["id"] == est_id and e["materia_id"] == mat_id for e in materias.estudiantes_de_docente(g.usuario["id"]))
    if not permitido:
        flash("Ese estudiante no está inscrito en tus materias.", "error")
    elif len(tema) < 4:
        flash("Escribe el tema que debe reforzar (mínimo 4 letras).", "error")
    else:
        solicitudes.crear(est_id, mat_id, tema, date.today().isoformat(), "Remitido por el docente.", remitida_por=g.usuario["id"])
        flash("Estudiante remitido a monitoría.", "ok")
    return redirect(url_for("docente.panel"))


@bp.route("/historial")
@rol_requerido("docente")
def historial():
    materia_id = request.args.get("materia", type=int)
    filas, pag = paginado(solicitudes.historial_docente, docente_id=g.usuario["id"], materia_id=materia_id, texto=request.args.get("q", "").strip())
    return render_template(
        "docente/historial.html", filas=filas, pag=pag,
        materias=materias.de_docente(g.usuario["id"]), materia_id=materia_id,
    )
