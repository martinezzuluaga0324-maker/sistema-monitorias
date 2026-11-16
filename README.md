# Tándem · Sistema de Monitorías Académicas

Aplicación web Full Stack hecha con **Python + Flask**, **SQLite**, **HTML5 / CSS3 / JavaScript**.
Proyecto final de *Herramientas Computacionales* (Ingeniería de Sistemas, 2026-2).

## El problema

Pedir una monitoría hoy depende de grupos de chat y de conocer a la persona indicada. No hay registro de quién
atendió a quién, ni de qué temas se vieron, y Bienestar Institucional no tiene cifras para decidir.

**Tándem** conecta a cuatro perfiles en un solo lugar: estudiantes, monitores, docentes y Bienestar Institucional.

## Objetivos

- Permitir que un estudiante solicite una monitoría indicando materia, tema y fecha.
- Publicar la disponibilidad de los monitores para que se les encuentre fácil.
- Registrar asistencia y temas vistos en cada sesión.
- Dar a Bienestar la asignación de monitores y reportes filtrables.

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3, Flask (Blueprints, Jinja2) |
| Base de datos | SQLite (módulo `sqlite3` de Python, SQL escrito a mano) |
| Frontend | HTML5 semántico, CSS3, JavaScript (eventos, validación, `fetch`) |
| Animaciones (portada) | GSAP + ScrollTrigger + Lenis (por CDN) |
| Seguridad | Contraseñas con hash (Werkzeug), sesiones de Flask, token CSRF, permisos por rol |

## Arquitectura (MVC)

```
sistema-monitorias/
├── app.py                 # Crea la app Flask, registra controladores y páginas de error
├── config.py              # Configuración (lee el archivo .env)
├── database.py            # Conexión a SQLite por petición
├── schema.sql             # Modelo relacional (tablas, llaves primarias y foráneas)
├── init_db.py             # Crea la base de datos y carga datos de ejemplo
├── requirements.txt
├── .env.example           # Guía de conexión / variables de entorno
├── models/                # M: consultas a la base de datos
│   ├── usuario.py  materia.py  disponibilidad.py  solicitud.py
├── controllers/           # C: rutas, validaciones y permisos
│   ├── publico.py  auth.py  estudiante.py  monitor.py  docente.py  bienestar.py
│   └── utils.py           # sesión, roles, CSRF y validaciones del servidor
├── templates/             # V: vistas HTML (Jinja2)
│   ├── base.html  app_base.html  index.html  error.html  _macros.html
│   └── auth/  estudiante/  monitor/  docente/  bienestar/
└── static/
    ├── css/  landing.css (portada)  app.css (pantallas internas)
    └── js/   landing.js  validacion.js  reportes.js
```

## Modelo de datos

```
usuarios ──< inscripciones >── materias
usuarios ──< monitor_materias >── materias
usuarios ──< disponibilidades
usuarios ──< solicitudes >── materias         (estudiante, monitor y docente que remite)
solicitudes ── sesiones                       (una sesión por solicitud)
```

Llaves primarias en todas las tablas, llaves foráneas con `ON DELETE` definido, `UNIQUE` en correo y código,
y `CHECK` para roles, estados y horarios. Las llaves foráneas se activan con `PRAGMA foreign_keys = ON`.

## Instalación

Requiere Python 3.10 o superior.

```bash
# 1. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Variables de entorno
copy .env.example .env         # Windows   (cp .env.example .env en Linux / macOS)

# 4. Crear la base de datos con datos de ejemplo
python init_db.py

# 5. Ejecutar
python app.py
```

Abre <http://127.0.0.1:5000>.

## Usuarios de ejemplo

Contraseña de todos: `Tandem2026!`

| Rol | Correo |
|---|---|
| Bienestar Institucional | bienestar@tandem.edu |
| Docente | docente.calculo@tandem.edu |
| Monitor | camila@tandem.edu · andres@tandem.edu |
| Estudiante | laura@tandem.edu |

Un estudiante nuevo puede crear su cuenta en `/registro`. Monitores y docentes los crea Bienestar en *Usuarios*.

## Qué hace cada rol (historias de usuario)

| Rol | Historias | Dónde |
|---|---|---|
| Estudiante | HU-1 a HU-4 | `/registro`, `/login`, `/estudiante/` (solicitar, editar, cancelar, eliminar, ver monitores) |
| Monitor | HU-5, HU-6 | `/monitor/` (CRUD de franjas y registro de sesión) |
| Docente | HU-7, HU-8 | `/docente/` (remitir) y `/docente/historial` |
| Bienestar | HU-9, HU-10 | `/bienestar/` (asignar), `/bienestar/reportes`, CRUD de usuarios y materias |

## Requisitos de los lineamientos y dónde verlos

- **CRUD completo:** solicitudes (estudiante), franjas de disponibilidad (monitor), usuarios y materias (Bienestar).
- **Consulta y visualización:** reportes con filtros y búsqueda dinámica (`/bienestar/reportes`), buscador de monitores.
- **Validaciones:** en el navegador (`static/js/validacion.js`) y de nuevo en el servidor (`controllers/utils.py`).
- **Consumo de datos del backend con `fetch`:** `/api/monitores` (portada) y `/bienestar/api/reportes`.
- **Manejo de errores:** páginas 400, 403, 404 y 500; mensajes de error por campo; avisos al usuario.
- **Interacción cliente-servidor:** formularios POST con CSRF y consultas JSON con `fetch`.

## Autores

Equipo del proyecto final · Ingeniería de Sistemas.

## Guía de funcionamiento

En `docs/Guia_de_funcionamiento_Tandem.pdf` y `docs/Manual_de_usuario_y_presentacion_Tandem.pdf` hay una guía completa: arquitectura, base de datos, seguridad, guion de la demostración y preguntas probables de la sustentación.
