import sqlite3

DATABASE = "inventario.db"

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

# Crear tabla productos con columna stock
cur.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER DEFAULT 0
    )
""")

# Si ya existe la tabla pero no la columna 'stock', la agrega
try:
    cur.execute("ALTER TABLE productos ADD COLUMN stock INTEGER DEFAULT 0")
    print("Columna 'stock' agregada a productos.")
except sqlite3.OperationalError:
    pass  # Ya existe

# Crear tabla ventas
cur.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        total REAL NOT NULL
    )
""")

# Crear tabla detalles de venta
cur.execute("""
    CREATE TABLE IF NOT EXISTS detalles_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER,
        producto_id INTEGER,
        nombre TEXT,
        cantidad INTEGER,
        precio_unitario REAL,
        FOREIGN KEY (venta_id) REFERENCES ventas(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    )
""")

conn.commit()
conn.close()
print("¡Base de datos inicializada correctamente!")