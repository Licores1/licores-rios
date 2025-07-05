import sqlite3

conn = sqlite3.connect("inventario.db")
cur = conn.cursor()

# Verifica si ya existe la columna 'nombre'
cur.execute("PRAGMA table_info(usuarios)")
columns = [row[1] for row in cur.fetchall()]
if "nombre" not in columns:
    cur.execute("ALTER TABLE usuarios ADD COLUMN nombre TEXT")
    print("Columna 'nombre' agregada.")
else:
    print("La columna 'nombre' ya existe.")

conn.commit()
conn.close()