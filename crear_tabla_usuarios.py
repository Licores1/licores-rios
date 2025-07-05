import sqlite3

def crear_tabla_usuarios():
    conn = sqlite3.connect("inventario.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('admin', 'vendedor'))
    );
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_tabla_usuarios()
    print("Tabla 'usuarios' creada o verificada.")