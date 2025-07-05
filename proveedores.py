import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

DATABASE = "inventario.db"

def crear_tabla_proveedores():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT
        )
    """)
    conn.commit()
    conn.close()

def ventana_gestion_proveedores():
    crear_tabla_proveedores()
    win = tk.Toplevel()
    win.title("Gestión de Proveedores")
    win.geometry("700x400")

    # Tabla de proveedores
    columns = ("ID", "Nombre", "Teléfono", "Email")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120 if col != "Nombre" else 200)
    tree.pack(fill="both", expand=True, pady=10, padx=10)

    def cargar_proveedores():
        tree.delete(*tree.get_children())
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, telefono, email FROM proveedores")
        for row in cur.fetchall():
            tree.insert("", tk.END, values=row)
        conn.close()

    cargar_proveedores()

    # Formulario para agregar/modificar
    frame = tk.Frame(win)
    frame.pack(pady=8)
    tk.Label(frame, text="Nombre:").grid(row=0, column=0, sticky="e")
    entry_nombre = tk.Entry(frame, width=28)
    entry_nombre.grid(row=0, column=1)
    tk.Label(frame, text="Teléfono:").grid(row=0, column=2, sticky="e")
    entry_telefono = tk.Entry(frame, width=18)
    entry_telefono.grid(row=0, column=3)
    tk.Label(frame, text="Email:").grid(row=0, column=4, sticky="e")
    entry_email = tk.Entry(frame, width=24)
    entry_email.grid(row=0, column=5)

    def limpiar_formulario():
        entry_nombre.delete(0, tk.END)
        entry_telefono.delete(0, tk.END)
        entry_email.delete(0, tk.END)

    def agregar_proveedor():
        nombre = entry_nombre.get().strip()
        telefono = entry_telefono.get().strip()
        email = entry_email.get().strip()
        if not nombre:
            messagebox.showwarning("Campos requeridos", "El nombre es obligatorio.")
            return
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("INSERT INTO proveedores (nombre, telefono, email) VALUES (?, ?, ?)",
                    (nombre, telefono, email))
        conn.commit()
        conn.close()
        limpiar_formulario()
        cargar_proveedores()
        messagebox.showinfo("Éxito", "Proveedor agregado correctamente.")

    def eliminar_proveedor():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona un proveedor para eliminar.")
            return
        prov_id = tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar este proveedor?"):
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("DELETE FROM proveedores WHERE id = ?", (prov_id,))
            conn.commit()
            conn.close()
            cargar_proveedores()

    def cargar_a_formulario():
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Selecciona un proveedor para modificar.")
            return
        prov = tree.item(sel[0])["values"]
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, prov[1])
        entry_telefono.delete(0, tk.END)
        entry_telefono.insert(0, prov[2])
        entry_email.delete(0, tk.END)
        entry_email.insert(0, prov[3])

    def modificar_proveedor():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona un proveedor para modificar.")
            return
        prov_id = tree.item(sel[0])["values"][0]
        nombre = entry_nombre.get().strip()
        telefono = entry_telefono.get().strip()
        email = entry_email.get().strip()
        if not nombre:
            messagebox.showwarning("Campos requeridos", "El nombre es obligatorio.")
            return
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("UPDATE proveedores SET nombre=?, telefono=?, email=? WHERE id=?",
                    (nombre, telefono, email, prov_id))
        conn.commit()
        conn.close()
        limpiar_formulario()
        cargar_proveedores()
        messagebox.showinfo("Éxito", "Proveedor modificado correctamente.")

    # Botones
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=7)
    tk.Button(btn_frame, text="Agregar", command=agregar_proveedor, bg="#4CAF50", fg="white", width=12).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Modificar", command=modificar_proveedor, bg="#2196F3", fg="white", width=12).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Cargar datos", command=cargar_a_formulario, bg="#FFB300", fg="black", width=12).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Eliminar", command=eliminar_proveedor, bg="#F44336", fg="white", width=12).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Limpiar", command=limpiar_formulario, width=12).pack(side="left", padx=5)

if __name__ == "__main__":
    ventana_gestion_proveedores()