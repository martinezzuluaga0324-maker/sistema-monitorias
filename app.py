"""Punto de entrada de la aplicación Flask.

Ejecutar:  python app.py   →  http://127.0.0.1:5000
"""
from flask import Flask, render_template, g

import database
from config import Config
from controllers import publico, auth, estudiante, monitor, docente, bienestar
from controllers.utils import cargar_usuario, verificar_csrf, token_csrf


def crear_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    database.init_app(app)

    # Antes de cada petición: saber quién es el usuario y revisar el token CSRF en los POST.
    app.before_request(cargar_usuario)
    app.before_request(verificar_csrf)

    # Variables disponibles en todas las plantillas.
    @app.context_processor
    def globales():
        return {"usuario": g.get("usuario")}

    # csrf_token() debe verse también dentro de los macros (_macros.html), por eso es global de Jinja.
    app.jinja_env.globals["csrf_token"] = token_csrf

    # Controladores (cada Blueprint agrupa las rutas de un rol).
    for modulo in (publico, auth, estudiante, monitor, docente, bienestar):
        app.register_blueprint(modulo.bp)

    # Páginas de error amigables.
    @app.errorhandler(400)
    def error_400(_e):
        return render_template("error.html", codigo=400, mensaje="La solicitud no es válida. Recarga la página e inténtalo de nuevo."), 400

    @app.errorhandler(403)
    def error_403(_e):
        return render_template("error.html", codigo=403, mensaje="No tienes permiso para ver esta página."), 403

    @app.errorhandler(404)
    def error_404(_e):
        return render_template("error.html", codigo=404, mensaje="No encontramos lo que buscas."), 404

    @app.errorhandler(500)
    def error_500(_e):
        return render_template("error.html", codigo=500, mensaje="Algo salió mal de nuestro lado. Inténtalo de nuevo."), 500

    return app


app = crear_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
