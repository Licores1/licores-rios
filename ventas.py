import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DATABASE = "inventario.db"

class VentaActual:
    def __init__(self):
        # Cada item: (id, nombre, cantidad, precio_venta, precio_compra)
        self.items = []

    def agregar(self, prod_id, nombre, cantidad, precio_venta, precio_compra):
        cantidad = int(cantidad)
        precio_venta = float(precio_venta)
        precio_compra = float(precio_compra)
        for item in self.items:
            if item[0] == prod_id:
                return False
        self.items.append((prod_id, nombre, cantidad, precio_venta, precio_compra))
        return True

    def quitar(self, prod_id):
        self.items = [item for item in self.items if item[0] != prod_id]

    def total(self):
        return sum(cant * precio_venta for _, _, cant, precio_venta, _ in self.items)

    def ganancia_total(self):
        return sum((precio_venta - precio_compra) * cant for _, _, cant, precio_venta, precio_compra in self.items)

def calcular_ganancia_unitaria(precio_compra, precio_venta):
    if precio_compra == 0:
        return 0.0
    return round(((precio_venta - precio_compra) / precio_compra) * 100, 2)

def registrar_venta_window(usuario="admin"):
    win = tk.Toplevel()
    win.title("Registrar Venta")
    win.geometry("850x550")

    venta = VentaActual()

    # Tabla de productos
    frame_prod = tk.Frame(win)
    frame_prod.pack(pady=10, fill="x")
    tk.Label(frame_prod, text="Buscar producto:").pack(side="left")
    entry_buscar = tk.Entry(frame_prod)
    entry_buscar.pack(side="left", padx=5)

    def cargar_productos(filtro=""):
        tree_prod.delete(*tree_prod.get_children())
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        # NUEVO: leer precio_compra y precio_venta
        if filtro:
            cur.execute("SELECT id, nombre, precio, stock, precio_compra FROM productos WHERE nombre LIKE ?", ('%'+filtro+'%',))
        else:
            cur.execute("SELECT id, nombre, precio, stock, precio_compra FROM productos")
        for p in cur.fetchall():
            tree_prod.insert("", tk.END, values=p)
        conn.close()

    tree_prod = ttk.Treeview(win, columns=("ID", "Nombre", "Precio Venta", "Stock", "Precio Compra"), show="headings", height=7)
    for col in ("ID", "Nombre", "Precio Venta", "Stock", "Precio Compra"):
        tree_prod.heading(col, text=col)
    tree_prod.pack(fill="x", padx=10)
    cargar_productos()

    def buscar():
        cargar_productos(entry_buscar.get().strip())
    tk.Button(frame_prod, text="Buscar", command=buscar).pack(side="left")

    # Frame para agregar producto a la venta
    frame_add = tk.Frame(win)
    frame_add.pack(pady=10)
    tk.Label(frame_add, text="Cantidad:").pack(side="left")
    entry_cant = tk.Entry(frame_add, width=5)
    entry_cant.pack(side="left", padx=5)

    def agregar_producto():
        sel = tree_prod.selection()
        if not sel:
            messagebox.showwarning("Selecciona producto", "Selecciona un producto")
            return
        try:
            cantidad = int(entry_cant.get())
            if cantidad <= 0:
                raise ValueError
        except:
            messagebox.showwarning("Cantidad inválida", "Ingresa cantidad válida")
            return
        prod = tree_prod.item(sel[0])["values"]
        prod_id = prod[0]
        nombre = prod[1]
        precio_venta = float(prod[2])
        stock = int(prod[3])
        precio_compra = float(prod[4])
        if cantidad > stock:
            messagebox.showwarning("Stock insuficiente", "No hay suficiente stock")
            return
        if venta.agregar(prod_id, nombre, cantidad, precio_venta, precio_compra):
            actualizar_items()
        else:
            messagebox.showinfo("Ya agregado", "El producto ya está en la venta")
    tk.Button(frame_add, text="Agregar a venta", command=agregar_producto).pack(side="left", padx=5)

    # Tabla de items en venta con ganancia
    tk.Label(win, text="Productos en venta:").pack()
    tree_items = ttk.Treeview(
        win,
        columns=("ID", "Nombre", "Cantidad", "Precio U", "Precio Compra", "Subtotal", "Ganancia %"),
        show="headings", height=5
    )
    for col in ("ID", "Nombre", "Cantidad", "Precio U", "Precio Compra", "Subtotal", "Ganancia %"):
        tree_items.heading(col, text=col)
    tree_items.pack(fill="x", padx=10)

    def actualizar_items():
        tree_items.delete(*tree_items.get_children())
        for item in venta.items:
            subtotal = item[2] * item[3]
            ganancia_porc = calcular_ganancia_unitaria(item[4], item[3])
            tree_items.insert("", tk.END, values=(
                item[0], item[1], item[2], item[3], item[4], subtotal, f"{ganancia_porc:.2f}%"
            ))
        label_total.config(text=f"Total: $ {venta.total():,.2f}   |   Ganancia: $ {venta.ganancia_total():,.2f}")

    def quitar_item():
        sel = tree_items.selection()
        if not sel:
            return
        prod_id = tree_items.item(sel[0])["values"][0]
        venta.quitar(prod_id)
        actualizar_items()
    tk.Button(win, text="Quitar producto", command=quitar_item).pack(pady=3)

    # Total
    label_total = tk.Label(win, text="Total: $ 0.00", font=("Arial", 14, "bold"))
    label_total.pack(pady=10)

    def registrar_venta():
        if not venta.items:
            messagebox.showwarning("Sin productos", "Agrega productos a la venta")
            return
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = venta.total()
        ganancia = venta.ganancia_total()
        # Guardar venta
        cur.execute("INSERT INTO ventas (fecha, total, ganancia, usuario) VALUES (?, ?, ?, ?)", (fecha, total, ganancia, usuario))
        venta_id = cur.lastrowid
        # Guardar detalles y actualizar stock
        for item in venta.items:
            cur.execute(
                "INSERT INTO detalles_venta (venta_id, producto_id, nombre, cantidad, precio_unitario, precio_compra, ganancia_unitaria) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (venta_id, item[0], item[1], item[2], item[3], item[4], calcular_ganancia_unitaria(item[4], item[3]))
            )
            cur.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (item[2], item[0]))
        # Sumar a caja
        cur.execute(
            "INSERT INTO caja (tipo, monto, descripcion, fecha) VALUES (?, ?, ?, ?)",
            ("ingreso", total, f"Venta ID {venta_id}", fecha)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Venta registrada", "¡Venta registrada correctamente!")
        win.destroy()
    tk.Button(win, text="Registrar venta", command=registrar_venta, bg="#4CAF50", fg="white").pack(pady=8)

def historial_ventas_window():
    win = tk.Toplevel()
    win.title("Historial de Ventas")
    win.geometry("700x400")
    frame = tk.Frame(win)
    frame.pack(fill="x", pady=10)
    tk.Label(frame, text="Buscar por fecha (YYYY-MM-DD):").pack(side="left")
    entry_fecha = tk.Entry(frame)
    entry_fecha.pack(side="left", padx=5)
    tree = ttk.Treeview(win, columns=("ID", "Fecha", "Total"), show="headings")
    for col in ("ID", "Fecha", "Total"):
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True, padx=10)

    def cargar_ventas(fecha=""):
        tree.delete(*tree.get_children())
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        if fecha:
            cur.execute("SELECT id, fecha, total FROM ventas WHERE fecha LIKE ?", ('%'+fecha+'%',))
        else:
            cur.execute("SELECT id, fecha, total FROM ventas")
        for v in cur.fetchall():
            tree.insert("", tk.END, values=v)
        conn.close()
    cargar_ventas()
    def buscar():
        cargar_ventas(entry_fecha.get().strip())
    tk.Button(frame, text="Buscar", command=buscar).pack(side="left", padx=5)

    def ver_detalles():
        sel = tree.selection()
        if not sel:
            return
        venta_id = tree.item(sel[0])["values"][0]
        detalles_win = tk.Toplevel(win)
        detalles_win.title(f"Detalles venta {venta_id}")
        detalles_tree = ttk.Treeview(detalles_win, columns=("Producto", "Cantidad", "Precio U", "Precio Compra", "Ganancia %"), show="headings")
        for col in ("Producto", "Cantidad", "Precio U", "Precio Compra", "Ganancia %"):
            detalles_tree.heading(col, text=col)
        detalles_tree.pack(fill="both", expand=True, padx=10, pady=5)
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT nombre, cantidad, precio_unitario, precio_compra, ganancia_unitaria FROM detalles_venta WHERE venta_id = ?", (venta_id,))
        for det in cur.fetchall():
            detalles_tree.insert("", tk.END, values=det)
        conn.close()
    tk.Button(win, text="Ver detalles", command=ver_detalles).pack(pady=5)

def main():
    registrar_venta_window()
def ventana_ventas():
    main()