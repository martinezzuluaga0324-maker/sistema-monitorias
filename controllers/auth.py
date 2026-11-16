"""Registro, inicio y cierre de sesión (HU-1)."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g

import models.usuario as usuarios
import models.materia as materias
from controllers.utils import validar_usuario, ids_de, INICIO_POR_ROL

bp = Blueprint("auth", __name__)


@bp.route("/registro", methods=["GET", "POST"])
def registro():
    """Solo los estudiantes se registran solos. Monitores y docentes los crea Bienestar."""
    if g.usuario:
        return redirect(url_for(INICIO_POR_ROL[g.usuario["rol"]]))
    errores, datos = {}, request.form
    if request.method == "POST":
        errores = validar_usuario({**request.form, "rol": "estudiante"})
        if "correo" not in errores and usuarios.por_correo(request.form["correo"]):
            errores["correo"] = "Ese correo ya está registrado."
        if "codigo" not in errores and usuarios.por_codigo(request.form["codigo"].strip()):
            errores["codigo"] = "Ese código ya está registrado."
        if not errores:
            uid = usuarios.crear(
                request.form["nombre"].strip(), request.form["codigo"].strip(), request.form["correo"].strip(),
                request.form["clave"], "estudiante", request.form.get("programa", "").strip(),
            )
            materias.fijar_inscripciones(uid, ids_de(request.form.getlist("materias")))
            session["usuario_id"] = uid
            flash("¡Bienvenido a Tándem! Tu cuenta quedó creada.", "ok")
            return redirect(url_for("estudiante.panel"))
    return render_template("auth/registro.html", errores=errores, datos=datos, materias=materias.listar())


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.usuario:
        return redirect(url_for(INICIO_POR_ROL[g.usuario["rol"]]))
    error = None
    if request.method == "POST":
        u = usuarios.verificar(request.form.get("correo", ""), request.form.get("clave", ""))
        if u:
            session.clear()                      # evita reutilizar una sesión anterior
            session["usuario_id"] = u["id"]
            destino = request.args.get("siguiente", "")
            # Solo se aceptan rutas internas, para que nadie nos redirija a otra web.
            if destino.startswith("/") and not destino.startswith("//"):
                return redirect(destino)
            return redirect(url_for(INICIO_POR_ROL[u["rol"]]))
        error = "Correo o contraseña incorrectos."
    return render_template("auth/login.html", error=error)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Cerraste sesión.", "ok")
    return redirect(url_for("publico.inicio"))
