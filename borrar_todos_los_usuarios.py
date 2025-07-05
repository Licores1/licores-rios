import sqlite3

conn = sqlite3.connect("inventario.db")
cur = conn.cursor()

cur.execute("DELETE FROM usuarios")
conn.commit()
print("¡Todos los usuarios han sido borrados!")

conn.close()