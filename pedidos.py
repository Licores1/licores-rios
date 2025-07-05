import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

DATABASE = "inventario.db"

def crear_tablas():
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            proveedor_id INTEGER NOT NULL,
            estado TEXT NOT NULL,
            comentarios TEXT,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS detalle_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_compra REAL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)
    conn.commit()
    conn.close()

def ventana_pedidos():
    win = tk.Toplevel()
    win.title("Pedidos a Proveedores")
    win.geometry("900x470")

    notebook = ttk.Notebook(win)
    notebook.pack(expand=True, fill="both")

    # TAB 1: Realizar pedido nuevo
    tab_nuevo = tk.Frame(notebook)
    notebook.add(tab_nuevo, text="Nuevo Pedido")

    # Sugerir productos bajos de stock
    def cargar_bajo_stock():
        tree_bajo_stock.delete(*tree_bajo_stock.get_children())
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, cantidad, stock_minimo FROM productos WHERE cantidad < stock_minimo")
        for row in cur.fetchall():
            tree_bajo_stock.insert("", tk.END, values=row)
        conn.close()

    tk.Label(tab_nuevo, text="Productos con bajo stock:").pack()
    tree_bajo_stock = ttk.Treeview(tab_nuevo, columns=("ID", "Producto", "Stock Actual", "Stock Mínimo"), show="headings", height=5)
    for col in ("ID", "Producto", "Stock Actual", "Stock Mínimo"):
        tree_bajo_stock.heading(col, text=col)
        tree_bajo_stock.column(col, width=120)
    tree_bajo_stock.pack(fill="x", padx=10)
    cargar_bajo_stock()

    # Selección de proveedor
    frame_prov = tk.Frame(tab_nuevo)
    frame_prov.pack(pady=10)
    tk.Label(frame_prov, text="Proveedor:").pack(side="left")
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM proveedores")
    proveedores = cur.fetchall()
    conn.close()
    prov_var = tk.StringVar()
    combo_prov = ttk.Combobox(frame_prov, values=[f"{pid} - {nombre}" for pid, nombre in proveedores], textvariable=prov_var, width=40)
    combo_prov.pack(side="left", padx=8)

    # Agregar productos al pedido
    pedido_items = []
    frame_add = tk.Frame(tab_nuevo)
    frame_add.pack(pady=5)
    tk.Button(frame_add, text="Agregar producto seleccionado", command=lambda: agregar_a_pedido()).pack(side="left", padx=8)
    tk.Button(frame_add, text="Quitar producto", command=lambda: quitar_de_pedido()).pack(side="left", padx=8)

    tree_pedido = ttk.Treeview(tab_nuevo, columns=("ID", "Producto", "Cantidad"), show="headings", height=5)
    for col in ("ID", "Producto", "Cantidad"):
        tree_pedido.heading(col, text=col)
        tree_pedido.column(col, width=130)
    tree_pedido.pack(fill="x", padx=10, pady=5)

    def agregar_a_pedido():
        sel = tree_bajo_stock.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Selecciona un producto con bajo stock.")
            return
        prod = tree_bajo_stock.item(sel[0])["values"]
        prod_id = prod[0]
        nombre = prod[1]
        # Solicitar cantidad al usuario
        cantidad = simpledialog.askinteger("Cantidad", f"Ingrese cantidad a pedir para '{nombre}':", minvalue=1)
        if cantidad:
            pedido_items.append((prod_id, nombre, cantidad))
            actualizar_tree_pedido()

    def quitar_de_pedido():
        sel = tree_pedido.selection()
        if not sel:
            return
        idx = tree_pedido.index(sel[0])
        del pedido_items[idx]
        actualizar_tree_pedido()

    def actualizar_tree_pedido():
        tree_pedido.delete(*tree_pedido.get_children())
        for prod_id, nombre, cantidad in pedido_items:
            tree_pedido.insert("", "end", values=(prod_id, nombre, cantidad))

    # Registrar pedido
    def registrar_pedido():
        if not pedido_items:
            messagebox.showwarning("Sin productos", "Agrega productos al pedido.")
            return
        if not prov_var.get():
            messagebox.showwarning("Proveedor", "Selecciona un proveedor.")
            return
        proveedor_id = int(prov_var.get().split(" - ")[0])
        comentarios = simpledialog.askstring("Comentarios", "Comentarios para el pedido (opcional):")
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO pedidos (fecha, proveedor_id, estado, comentarios) VALUES (?, ?, ?, ?)",
                    (fecha, proveedor_id, "pendiente", comentarios))
        pedido_id = cur.lastrowid
        for prod_id, nombre, cantidad in pedido_items:
            cur.execute("INSERT INTO detalle_pedido (pedido_id, producto_id, cantidad) VALUES (?, ?, ?)",
                        (pedido_id, prod_id, cantidad))
        conn.commit()
        conn.close()
        messagebox.showinfo("Pedido registrado", "¡Pedido registrado correctamente!")
        pedido_items.clear()
        actualizar_tree_pedido()
        cargar_bajo_stock()
        cargar_pedidos_pendientes()

    tk.Button(tab_nuevo, text="Registrar pedido", command=registrar_pedido, bg="#4CAF50", fg="white").pack(pady=10)

    # TAB 2: Pedidos pendientes y recepción
    tab_pendientes = tk.Frame(notebook)
    notebook.add(tab_pendientes, text="Pedidos Pendientes")

    tree_pedidos = ttk.Treeview(tab_pendientes, columns=("ID", "Fecha", "Proveedor", "Estado", "Comentarios"), show="headings", height=6)
    for col in ("ID", "Fecha", "Proveedor", "Estado", "Comentarios"):
        tree_pedidos.heading(col, text=col)
        tree_pedidos.column(col, width=120 if col != "Comentarios" else 200)
    tree_pedidos.pack(fill="x", padx=10, pady=10)

    def cargar_pedidos_pendientes():
        tree_pedidos.delete(*tree_pedidos.get_children())
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.fecha, pr.nombre, p.estado, p.comentarios
            FROM pedidos p
            JOIN proveedores pr ON p.proveedor_id = pr.id
            WHERE p.estado != 'recibido'
            ORDER BY p.fecha DESC
        """)
        for row in cur.fetchall():
            tree_pedidos.insert("", tk.END, values=row)
        conn.close()
    cargar_pedidos_pendientes()

    # Ver detalle y recibir pedido
    def ver_detalle_y_recibir():
        sel = tree_pedidos.selection()
        if not sel:
            messagebox.showinfo("Selecciona", "Selecciona un pedido para ver detalles o recibir.")
            return
        pedido_id = tree_pedidos.item(sel[0])["values"][0]
        win_det = tk.Toplevel(win)
        win_det.title(f"Detalle del pedido {pedido_id}")
        win_det.geometry("500x350")
        tree_det = ttk.Treeview(win_det, columns=("Producto", "Cantidad pedida"), show="headings")
        for col in ("Producto", "Cantidad pedida"):
            tree_det.heading(col, text=col)
            tree_det.column(col, width=200)
        tree_det.pack(fill="both", expand=True, padx=10, pady=10)

        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("""
            SELECT productos.nombre, dp.cantidad
            FROM detalle_pedido dp
            JOIN productos ON dp.producto_id = productos.id
            WHERE dp.pedido_id = ?
        """, (pedido_id,))
        detalles = cur.fetchall()
        for det in detalles:
            tree_det.insert("", tk.END, values=det)
        conn.close()

        def recibir():
            if messagebox.askyesno("Confirmar", "¿Marcar este pedido como recibido y sumar al inventario?"):
                conn = sqlite3.connect(DATABASE)
                cur = conn.cursor()
                for nombre, cant in detalles:
                    # Suma la cantidad recibida al inventario
                    cur.execute("UPDATE productos SET cantidad = cantidad + ? WHERE nombre = ?", (cant, nombre))
                cur.execute("UPDATE pedidos SET estado = 'recibido' WHERE id = ?", (pedido_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("¡Listo!", "Pedido recibido y stock actualizado.")
                win_det.destroy()
                cargar_pedidos_pendientes()
                cargar_bajo_stock()

        tk.Button(win_det, text="Recibir pedido y actualizar inventario", command=recibir, bg="#4CAF50", fg="white").pack(pady=8)

    tk.Button(tab_pendientes, text="Ver detalle / Recibir pedido", command=ver_detalle_y_recibir, bg="#2196F3", fg="white").pack(pady=8)

    # TAB 3: Historial de pedidos
    tab_historial = tk.Frame(notebook)
    notebook.add(tab_historial, text="Historial de Pedidos")

    tree_hist = ttk.Treeview(tab_historial, columns=("ID", "Fecha", "Proveedor", "Estado", "Comentarios"), show="headings", height=10)
    for col in ("ID", "Fecha", "Proveedor", "Estado", "Comentarios"):
        tree_hist.heading(col, text=col)
        tree_hist.column(col, width=120 if col != "Comentarios" else 200)
    tree_hist.pack(fill="both", expand=True, padx=10, pady=10)

    def cargar_historial():
        tree_hist.delete(*tree_hist.get_children())
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.fecha, pr.nombre, p.estado, p.comentarios
            FROM pedidos p
            JOIN proveedores pr ON p.proveedor_id = pr.id
            ORDER BY p.fecha DESC
        """)
        for row in cur.fetchall():
            tree_hist.insert("", tk.END, values=row)
        conn.close()
    cargar_historial()

if __name__ == "__main__":
    crear_tablas()
    ventana_pedidos()