import sqlite3

con = sqlite3.connect("inventario.db")  # Cambia el nombre si tu base es diferente
cur = con.cursor()

# Intenta agregar la columna stock_minimo solo si no existe
try:
    cur.execute("ALTER TABLE productos ADD COLUMN stock_minimo INTEGER DEFAULT 5")
    print("Columna 'stock_minimo' agregada exitosamente.")
except Exception as e:
    print("Puede que la columna ya exista o hubo otro problema:", e)

con.commit()
con.close()