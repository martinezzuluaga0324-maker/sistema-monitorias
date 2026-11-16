"""Páginas públicas: portada y búsqueda de monitores (HU-3)."""
from flask import Blueprint, render_template, request, jsonify

import models.materia as materias
import models.disponibilidad as disponibilidad

bp = Blueprint("publico", __name__)


@bp.route("/")
def inicio():
    return render_template(
        "index.html",
        materias=materias.listar(),
        monitores=disponibilidad.monitores_con_agenda(),
    )


@bp.route("/api/monitores")
def api_monitores():
    """Devuelve JSON; el JavaScript de la portada lo consulta con fetch() al cambiar el filtro."""
    materia_id = request.args.get("materia", type=int)
    texto = request.args.get("q", "").strip()
    return jsonify(disponibilidad.monitores_con_agenda(materia_id, texto))
