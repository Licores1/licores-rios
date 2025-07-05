import sqlite3

conn = sqlite3.connect("inventario.db")
cur = conn.cursor()

# Agregar columna categoria
try:
    cur.execute("ALTER TABLE productos ADD COLUMN categoria TEXT")
    print("Columna 'categoria' agregada.")
except sqlite3.OperationalError:
    print("Columna 'categoria' ya existe.")

# Agregar columna cantidad
try:
    cur.execute("ALTER TABLE productos ADD COLUMN cantidad INTEGER DEFAULT 0")
    print("Columna 'cantidad' agregada.")
except sqlite3.OperationalError:
    print("Columna 'cantidad' ya existe.")

# Agregar columna stock_minimo
try:
    cur.execute("ALTER TABLE productos ADD COLUMN stock_minimo INTEGER DEFAULT 0")
    print("Columna 'stock_minimo' agregada.")
except sqlite3.OperationalError:
    print("Columna 'stock_minimo' ya existe.")

conn.commit()
conn.close()
print("¡Todas las columnas listas!")