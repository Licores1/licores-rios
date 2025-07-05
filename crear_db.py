import sqlite3
import hashlib

usuarios_iniciales = [
    ("LicoresRios", "Rios2109", "admin"),
    ("yieisyRios", "Yieisy2025", "vendedor"),
]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect('inventario.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT,
    cantidad INTEGER NOT NULL,
    precio REAL NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    cantidad_vendida INTEGER NOT NULL,
    total REAL NOT NULL,
    fecha TEXT NOT NULL,
    vendedor TEXT NOT NULL,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('admin', 'vendedor'))
)
''')

for usuario, password, rol in usuarios_iniciales:
    password_hash = hash_password(password)
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios (usuario, password_hash, rol) VALUES (?, ?, ?)",
            (usuario, password_hash, rol)
        )

conn.commit()
conn.close()
print("✅ Base de datos 'inventario.db' creada y usuarios principales listos.")