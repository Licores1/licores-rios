import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def crear_admin():
    usuario = "admin"
    nombre = "Administrador"
    password = "admin123"   # Puedes cambiar esta contraseña si lo deseas
    rol = "admin"
    password_hash = hash_password(password)

    conn = sqlite3.connect("inventario.db")
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (usuario, nombre, password_hash, rol) VALUES (?, ?, ?, ?)",
            (usuario, nombre, password_hash, rol)
        )
        conn.commit()
        print("Usuario admin creado correctamente.")
    except sqlite3.IntegrityError:
        print("El usuario admin ya existe.")
    finally:
        conn.close()

if __name__ == "__main__":
    crear_admin()