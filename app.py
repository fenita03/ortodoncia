from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "1234"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
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

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]

        if user == "admin" and password == "1234":
            session["user"] = user
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =========================
# PACIENTES
# =========================

@app.route("/pacientes")
def pacientes():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    pacientes = conn.execute("SELECT * FROM pacientes ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("pacientes.html", pacientes=pacientes)

@app.route("/pacientes/nuevo", methods=["GET", "POST"])
def nuevo_paciente():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        dni = request.form["dni"]
        direccion = request.form["direccion"]
        observaciones = request.form["observaciones"]

        conn = get_db()
        conn.execute("""
            INSERT INTO pacientes (nombre, telefono, dni, direccion, observaciones)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, telefono, dni, direccion, observaciones))
        conn.commit()
        conn.close()

        return redirect("/pacientes")

    return render_template("pacientes_form.html", paciente=None)

@app.route("/pacientes/editar/<int:id>", methods=["GET", "POST"])
def editar_paciente(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    paciente = conn.execute("SELECT * FROM pacientes WHERE id = ?", (id,)).fetchone()

    if not paciente:
        conn.close()
        return "Paciente no encontrado"

    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        dni = request.form["dni"]
        direccion = request.form["direccion"]
        observaciones = request.form["observaciones"]

        conn.execute("""
            UPDATE pacientes
            SET nombre = ?, telefono = ?, dni = ?, direccion = ?, observaciones = ?
            WHERE id = ?
        """, (nombre, telefono, dni, direccion, observaciones, id))
        conn.commit()
        conn.close()

        return redirect("/pacientes")

    conn.close()
    return render_template("pacientes_form.html", paciente=paciente)

@app.route("/pacientes/eliminar/<int:id>")
def eliminar_paciente(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    conn.execute("DELETE FROM pacientes WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/pacientes")

# =========================
# GASTOS
# =========================

@app.route("/gastos")
def gastos():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    gastos = conn.execute("SELECT * FROM gastos ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("gastos.html", gastos=gastos)

@app.route("/gastos/nuevo", methods=["GET", "POST"])
def nuevo_gasto():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        fecha = request.form["fecha"]
        descripcion = request.form["descripcion"]
        categoria = request.form["categoria"]
        monto = request.form["monto"]

        conn = get_db()
        conn.execute("""
            INSERT INTO gastos (fecha, descripcion, categoria, monto)
            VALUES (?, ?, ?, ?)
        """, (fecha, descripcion, categoria, monto))
        conn.commit()
        conn.close()

        return redirect("/gastos")

    return render_template("gastos_form.html", gasto=None)

@app.route("/gastos/editar/<int:id>", methods=["GET", "POST"])
def editar_gasto(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    gasto = conn.execute("SELECT * FROM gastos WHERE id = ?", (id,)).fetchone()

    if not gasto:
        conn.close()
        return "Gasto no encontrado"

    if request.method == "POST":
        fecha = request.form["fecha"]
        descripcion = request.form["descripcion"]
        categoria = request.form["categoria"]
        monto = request.form["monto"]

        conn.execute("""
            UPDATE gastos
            SET fecha = ?, descripcion = ?, categoria = ?, monto = ?
            WHERE id = ?
        """, (fecha, descripcion, categoria, monto, id))
        conn.commit()
        conn.close()

        return redirect("/gastos")

    conn.close()
    return render_template("gastos_form.html", gasto=gasto)

@app.route("/gastos/eliminar/<int:id>")
def eliminar_gasto(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    conn.execute("DELETE FROM gastos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/gastos")

# =========================
# COBROS
# =========================

@app.route("/cobros")
def cobros():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cobros = conn.execute("""
        SELECT cobros.*, pacientes.nombre AS paciente_nombre
        FROM cobros
        INNER JOIN pacientes ON cobros.paciente_id = pacientes.id
        ORDER BY cobros.id DESC
    """).fetchall()
    conn.close()

    return render_template("cobros.html", cobros=cobros)

@app.route("/cobros/nuevo", methods=["GET", "POST"])
def nuevo_cobro():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    pacientes = conn.execute("SELECT * FROM pacientes ORDER BY nombre ASC").fetchall()

    if request.method == "POST":
        paciente_id = request.form["paciente_id"]
        fecha = request.form["fecha"]
        descripcion = request.form["descripcion"]
        metodo_pago = request.form["metodo_pago"]
        monto = request.form["monto"]

        conn.execute("""
            INSERT INTO cobros (paciente_id, fecha, descripcion, metodo_pago, monto)
            VALUES (?, ?, ?, ?, ?)
        """, (paciente_id, fecha, descripcion, metodo_pago, monto))
        conn.commit()
        conn.close()

        return redirect("/cobros")

    conn.close()
    return render_template("cobros_form.html", cobro=None, pacientes=pacientes)

@app.route("/cobros/editar/<int:id>", methods=["GET", "POST"])
def editar_cobro(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cobro = conn.execute("SELECT * FROM cobros WHERE id = ?", (id,)).fetchone()
    pacientes = conn.execute("SELECT * FROM pacientes ORDER BY nombre ASC").fetchall()

    if not cobro:
        conn.close()
        return "Cobro no encontrado"

    if request.method == "POST":
        paciente_id = request.form["paciente_id"]
        fecha = request.form["fecha"]
        descripcion = request.form["descripcion"]
        metodo_pago = request.form["metodo_pago"]
        monto = request.form["monto"]

        conn.execute("""
            UPDATE cobros
            SET paciente_id = ?, fecha = ?, descripcion = ?, metodo_pago = ?, monto = ?
            WHERE id = ?
        """, (paciente_id, fecha, descripcion, metodo_pago, monto, id))
        conn.commit()
        conn.close()

        return redirect("/cobros")

    conn.close()
    return render_template("cobros_form.html", cobro=cobro, pacientes=pacientes)

@app.route("/cobros/eliminar/<int:id>")
def eliminar_cobro(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    conn.execute("DELETE FROM cobros WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/cobros")
import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))