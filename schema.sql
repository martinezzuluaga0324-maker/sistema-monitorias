-- Modelo relacional de Tándem (SQLite).
-- Se ejecuta una sola vez con:  python init_db.py

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS sesiones;
DROP TABLE IF EXISTS solicitudes;
DROP TABLE IF EXISTS disponibilidades;
DROP TABLE IF EXISTS monitor_materias;
DROP TABLE IF EXISTS inscripciones;
DROP TABLE IF EXISTS materias;
DROP TABLE IF EXISTS usuarios;

-- Todas las personas del sistema. El campo "rol" define qué puede hacer cada una.
CREATE TABLE usuarios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL,
    codigo      TEXT UNIQUE,                       -- código estudiantil (solo estudiantes y monitores)
    correo      TEXT NOT NULL UNIQUE,
    clave_hash  TEXT NOT NULL,                     -- nunca se guarda la contraseña en claro
    rol         TEXT NOT NULL CHECK (rol IN ('estudiante', 'monitor', 'docente', 'bienestar')),
    programa    TEXT,
    creado_en   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Materias que tienen monitoría. Cada una la dicta un docente.
CREATE TABLE materias (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL UNIQUE,
    docente_id  INTEGER REFERENCES usuarios(id) ON DELETE SET NULL
);

-- Qué estudiantes están inscritos en qué materia (relación muchos a muchos).
CREATE TABLE inscripciones (
    estudiante_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    materia_id    INTEGER NOT NULL REFERENCES materias(id) ON DELETE CASCADE,
    PRIMARY KEY (estudiante_id, materia_id)
);

-- Qué materias puede atender cada monitor (relación muchos a muchos).
CREATE TABLE monitor_materias (
    monitor_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    materia_id INTEGER NOT NULL REFERENCES materias(id) ON DELETE CASCADE,
    PRIMARY KEY (monitor_id, materia_id)
);

-- Días y franjas horarias en las que el monitor está libre (HU-5).
CREATE TABLE disponibilidades (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_id  INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    dia         TEXT NOT NULL CHECK (dia IN ('Lunes','Martes','Miércoles','Jueves','Viernes','Sábado')),
    hora_inicio TEXT NOT NULL,                     -- formato HH:MM
    hora_fin    TEXT NOT NULL,
    CHECK (hora_fin > hora_inicio)
);

-- Pedido de monitoría que hace un estudiante (HU-2, HU-4, HU-7, HU-9).
CREATE TABLE solicitudes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id   INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    materia_id      INTEGER NOT NULL REFERENCES materias(id) ON DELETE RESTRICT,
    tema            TEXT NOT NULL,
    fecha_preferida TEXT NOT NULL,                 -- formato AAAA-MM-DD
    notas           TEXT,
    estado          TEXT NOT NULL DEFAULT 'pendiente'
                    CHECK (estado IN ('pendiente', 'asignada', 'atendida', 'cancelada')),
    monitor_id      INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
    remitida_por    INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,  -- docente que la remitió
    creado_en       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Registro de lo que pasó en la sesión (HU-6): una sesión por solicitud.
CREATE TABLE sesiones (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    solicitud_id  INTEGER NOT NULL UNIQUE REFERENCES solicitudes(id) ON DELETE CASCADE,
    asistio       INTEGER NOT NULL CHECK (asistio IN (0, 1)),
    temas_vistos  TEXT,
    registrada_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_solicitudes_estado ON solicitudes(estado);
CREATE INDEX idx_solicitudes_estudiante ON solicitudes(estudiante_id);
CREATE INDEX idx_disponibilidades_monitor ON disponibilidades(monitor_id);
