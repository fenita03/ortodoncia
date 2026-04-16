import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    telefono TEXT,
    dni TEXT,
    direccion TEXT,
    observaciones TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    categoria TEXT,
    monto REAL NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cobros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    descripcion TEXT,
    metodo_pago TEXT,
    monto REAL NOT NULL,
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
)
""")

conn.commit()
conn.close()

print("Base creada")