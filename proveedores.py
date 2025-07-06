import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import sqlite3

DB_NAME = 'inventario.db'

def obtener_productos():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM inventario")
    productos = cur.fetchall()
    conn.close()
    return productos

def obtener_productos_proveedor(proveedor_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT producto_id FROM proveedor_producto WHERE proveedor_id=?", (proveedor_id,))
    productos = [row[0] for row in cur.fetchall()]
    conn.close()
    return productos

def asociar_productos_a_proveedor(proveedor_id, lista_producto_ids):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM proveedor_producto WHERE proveedor_id=?", (proveedor_id,))
    for pid in lista_producto_ids:
        cur.execute("INSERT INTO proveedor_producto (proveedor_id, producto_id) VALUES (?, ?)", (proveedor_id, pid))
    conn.commit()
    conn.close()

def ventana_asociar_productos(proveedor_id, proveedor_nombre):
    win = tk.Toplevel()
    win.title(f"Productos de proveedor: {proveedor_nombre}")

    tk.Label(win, text="Selecciona los productos que suministra este proveedor:").pack()

    productos = obtener_productos()
    productos_asociados = obtener_productos_proveedor(proveedor_id)

    listbox = tk.Listbox(win, selectmode=tk.MULTIPLE, width=50)
    for idx, (pid, nombre) in enumerate(productos):
        listbox.insert(tk.END, nombre)
        if pid in productos_asociados:
            listbox.selection_set(idx)
    listbox.pack()

    def guardar_asociaciones():
        seleccionados = [productos[i][0] for i in listbox.curselection()]
        asociar_productos_a_proveedor(proveedor_id, seleccionados)
        messagebox.showinfo("Éxito", "Productos asociados correctamente.", parent=win)
        win.destroy()

    tk.Button(win, text="Guardar", command=guardar_asociaciones, bg="#1976D2", fg="white").pack(pady=10)

def get_productos():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT nombre FROM inventario")
    productos = [row[0] for row in cur.fetchall()]
    conn.close()
    return productos

def ventana_proveedores():
    win = tk.Toplevel()
    win.title("Gestión de Proveedores")
    win.geometry("800x450")

    def cargar_proveedores():
        for item in lista.get_children():
            lista.delete(item)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, telefono, email FROM proveedores")
        for row in cur.fetchall():
            lista.insert('', 'end', values=row)
        conn.close()

    def agregar_proveedor():
        nombre = simpledialog.askstring("Nombre", "Nombre del proveedor:", parent=win)
        if not nombre:
            return
        telefono = simpledialog.askstring("Teléfono", "Teléfono:", parent=win)
        email = simpledialog.askstring("Email", "Email:", parent=win)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO proveedores (nombre, telefono, email) VALUES (?,?,?)", (nombre, telefono, email))
        conn.commit()
        conn.close()
        cargar_proveedores()

    def eliminar_proveedor():
        item = lista.selection()
        if not item:
            return
        proveedor_id = lista.item(item, 'values')[0]
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("DELETE FROM proveedores WHERE id=?", (proveedor_id,))
        cur.execute("DELETE FROM proveedor_producto WHERE proveedor_id=?", (proveedor_id,))
        conn.commit()
        conn.close()
        cargar_proveedores()

    def realizar_pedido():
        item = lista.selection()
        if not item:
            messagebox.showwarning("Atención", "Seleccione un proveedor.", parent=win)
            return
        proveedor_id = lista.item(item, 'values')[0]
        nombre_prov = lista.item(item, 'values')[1]
        ventana_pedido(proveedor_id, nombre_prov)

    def ver_historial():
        item = lista.selection()
        if not item:
            messagebox.showwarning("Atención", "Seleccione un proveedor.", parent=win)
            return
        proveedor_id = lista.item(item, 'values')[0]
        nombre_prov = lista.item(item, 'values')[1]
        ventana_historial_pedidos(proveedor_id, nombre_prov)

    def asociar_productos():
        item = lista.selection()
        if not item:
            messagebox.showwarning("Atención", "Seleccione un proveedor.", parent=win)
            return
        proveedor_id = lista.item(item, 'values')[0]
        proveedor_nombre = lista.item(item, 'values')[1]
        ventana_asociar_productos(proveedor_id, proveedor_nombre)

    lista = ttk.Treeview(win, columns=("ID", "Nombre", "Teléfono", "Email"), show="headings")
    for col in ("ID", "Nombre", "Teléfono", "Email"):
        lista.heading(col, text=col)
        lista.column(col, minwidth=0, width=140, stretch=tk.NO)
    lista.pack(fill="both", expand=True, pady=10)

    frame = tk.Frame(win)
    frame.pack(pady=5)
    tk.Button(frame, text="Agregar Proveedor", command=agregar_proveedor, bg="#388E3C", fg="white").pack(side="left", padx=5)
    tk.Button(frame, text="Eliminar Proveedor", command=eliminar_proveedor, bg="#D32F2F", fg="white").pack(side="left", padx=5)
    tk.Button(frame, text="Realizar Pedido", command=realizar_pedido, bg="#1976D2", fg="white").pack(side="left", padx=5)
    tk.Button(frame, text="Historial de Pedidos", command=ver_historial, bg="#6A1B9A", fg="white").pack(side="left", padx=5)
    tk.Button(frame, text="Asociar Productos", command=asociar_productos, bg="#0097A7", fg="white").pack(side="left", padx=5)

    cargar_proveedores()

def ventana_pedido(proveedor_id, nombre_prov):
    win = tk.Toplevel()
    win.title(f"Realizar Pedido a {nombre_prov}")
    win.geometry("300x200")

    tk.Label(win, text=f"Pedido a: {nombre_prov}", font=("Arial", 12)).pack(pady=5)

    tk.Label(win, text="Producto:").pack()
    productos = get_productos()
    producto_var = tk.StringVar()
    cb = ttk.Combobox(win, textvariable=producto_var, values=productos, state="readonly")
    cb.pack(pady=2)

    tk.Label(win, text="Cantidad:").pack()
    cantidad = tk.Entry(win)
    cantidad.pack(pady=2)

    def guardar_pedido():
        prod = producto_var.get()
        cant = cantidad.get()
        if not prod or not cant:
            messagebox.showerror("Error", "Completa todos los campos.", parent=win)
            return
        try:
            cant_int = int(cant)
            if cant_int <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número positivo.", parent=win)
            return
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO pedidos (proveedor_id, producto, cantidad) VALUES (?,?,?)", (proveedor_id, prod, cant_int))
        conn.commit()
        conn.close()
        messagebox.showinfo("Pedido", "Pedido registrado correctamente.", parent=win)
        win.destroy()

    tk.Button(win, text="Guardar Pedido", command=guardar_pedido, bg="#1976D2", fg="white").pack(pady=10)

def ventana_historial_pedidos(proveedor_id, nombre_prov):
    win = tk.Toplevel()
    win.title(f"Historial de Pedidos a {nombre_prov}")
    win.geometry("500x300")

    tree = ttk.Treeview(win, columns=("ID", "Producto", "Cantidad", "Fecha"), show="headings")
    for col in ("ID", "Producto", "Cantidad", "Fecha"):
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True, pady=10)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, producto, cantidad, fecha FROM pedidos WHERE proveedor_id=? ORDER BY fecha DESC",
        (proveedor_id,)
    )
    for row in cur.fetchall():
        tree.insert('', 'end', values=row)
    conn.close()