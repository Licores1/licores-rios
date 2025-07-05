import sqlite3

conn = sqlite3.connect("inventario.db")
cur = conn.cursor()

# Productos de ejemplo (puedes editar o agregar los que quieras)
productos = [
    ("Ron Medellin", 48000, 10),
    ("Aguardiente Antioqueño", 32000, 20),
    ("Whisky Old Parr", 130000, 5),
    ("Cerveza Poker", 4000, 50),
    ("Vino Gato Negro", 25000, 15)
]

for nombre, precio, stock in productos:
    cur.execute(
        "INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
        (nombre, precio, stock)
    )

conn.commit()
conn.close()
print("¡Productos de ejemplo agregados!")