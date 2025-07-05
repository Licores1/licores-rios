import sqlite3
import hashlib

DATABASE = "inventario.db"

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def autenticar(usuario, password):
    password_hash = hash_password(password)
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT rol FROM usuarios WHERE usuario=? AND password_hash=?", (usuario, password_hash))
    result = cur.fetchone()
    conn.close()
    if result:
        return result[0]  # "admin" o "vendedor"
    else:
        return None

def obtener_usuarios():
    """Devuelve una lista de tuplas (id, usuario, nombre, rol) de todos los usuarios."""
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT id, usuario, nombre, rol FROM usuarios")
    usuarios = cur.fetchall()
    conn.close()
    return usuarios

def registrar_usuario(usuario, nombre, password, rol):
    """Registra un usuario. Devuelve True si lo logró, False si ya existe."""
    password_hash = hash_password(password)
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (usuario, nombre, password_hash, rol) VALUES (?, ?, ?, ?)",
                    (usuario, nombre, password_hash, rol))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def eliminar_usuario(usuario_id):
    """Elimina el usuario por id."""
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    conn.close()

# Si quieres seguir usando la ventana embebida en este archivo, puedes dejarla,
# pero lo ideal es que uses la ventana de gestionar_usuarios.py para evitar duplicidad.
def ventana_gestion_usuarios():
    import tkinter as tk
    from tkinter import ttk, messagebox

    win = tk.Toplevel()
    win.title("Gestión de Usuarios")
    win.geometry("600x400")

    tree = ttk.Treeview(win, columns=("ID", "Usuario", "Nombre", "Rol"), show="headings")
    for col in ("ID", "Usuario", "Nombre", "Rol"):
        tree.heading(col, text=col)
        tree.column(col, width=120 if col != "Nombre" else 180)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    frm = tk.Frame(win)
    frm.pack(pady=10)
    tk.Label(frm, text="Usuario:").grid(row=0, column=0)
    entry_usuario = tk.Entry(frm)
    entry_usuario.grid(row=0, column=1)
    tk.Label(frm, text="Nombre:").grid(row=0, column=2)
    entry_nombre = tk.Entry(frm)
    entry_nombre.grid(row=0, column=3)
    tk.Label(frm, text="Contraseña:").grid(row=1, column=0)
    entry_password = tk.Entry(frm, show="*")
    entry_password.grid(row=1, column=1)
    tk.Label(frm, text="Rol:").grid(row=1, column=2)
    combo_rol = ttk.Combobox(frm, values=["admin", "vendedor"], state="readonly")
    combo_rol.set("vendedor")
    combo_rol.grid(row=1, column=3)

    def refrescar():
        for row in tree.get_children():
            tree.delete(row)
        for u in obtener_usuarios():
            tree.insert("", tk.END, values=u)

    def agregar_usuario():
        usuario = entry_usuario.get().strip()
        nombre = entry_nombre.get().strip()
        password = entry_password.get().strip()
        rol = combo_rol.get()
        if not usuario or not nombre or not password or not rol:
            messagebox.showwarning("Campos requeridos", "Completa todos los campos.")
            return
        if registrar_usuario(usuario, nombre, password, rol):
            refrescar()
            entry_usuario.delete(0, tk.END)
            entry_nombre.delete(0, tk.END)
            entry_password.delete(0, tk.END)
            combo_rol.set("vendedor")
            messagebox.showinfo("Éxito", "Usuario registrado.")
        else:
            messagebox.showerror("Duplicado", "El usuario ya existe.")

    def eliminar_usuario_local():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona un usuario para eliminar.")
            return
        usuario_id = tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar usuario?"):
            eliminar_usuario(usuario_id)
            refrescar()

    btns = tk.Frame(win)
    btns.pack()
    tk.Button(btns, text="Agregar Usuario", command=agregar_usuario, bg="#2196F3", fg="white").pack(side="left", padx=10)
    tk.Button(btns, text="Eliminar Usuario", command=eliminar_usuario_local, bg="#F44336", fg="white").pack(side="left", padx=10)

    refrescar()