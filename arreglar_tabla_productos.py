import sqlite3

conn = sqlite3.connect("inventario.db")
cur = conn.cursor()

# Verificar columnas
cur.execute("PRAGMA table_info(productos)")
cols = [row[1] for row in cur.fetchall()]
print("Columnas de productos:", cols)

# Si existe 'cantidad' pero no 'stock', elimina 'cantidad'
if "cantidad" in cols:
    # SQLite no soporta DROP COLUMN directo, así que debes recrear la tabla
    # 1. Renombrar la tabla actual
    cur.execute("ALTER TABLE productos RENAME TO productos_old")
    # 2. Crear la nueva tabla SIN columna cantidad
    cur.execute("""
        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
    """)
    # 3. Copiar los datos de la antigua a la nueva (asumiendo 'cantidad' era el stock)
    cur.execute("INSERT INTO productos (id, nombre, precio, stock) SELECT id, nombre, precio, cantidad FROM productos_old")
    # 4. Borrar la tabla vieja
    cur.execute("DROP TABLE productos_old")
    conn.commit()
    print("La columna 'cantidad' ha sido reemplazada por 'stock'.")
else:
    print("La columna 'cantidad' no existe. No hay nada que arreglar.")

conn.close()