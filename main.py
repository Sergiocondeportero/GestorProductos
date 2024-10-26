from tkinter import ttk
from tkinter import *
from tkinter.ttk import Progressbar
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, declarative_base

# Definición de la base de datos con SQLAlchemy
Base = declarative_base()

class Producto(Base):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String, nullable=False)  # Nuevo campo de Categoría
    stock = db.Column(db.Integer, nullable=False)  # Nuevo campo de Stock

# Inicializar la base de datos
engine = db.create_engine('sqlite:///productos.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class VentanaPrincipal:
    def __init__(self, root):
        self.ventana = root
        self.ventana.title("App Gestor de Productos")
        self.ventana.geometry("600x500")  # Tamaño ajustado de la ventana
        self.ventana.resizable(1, 1)

        # Configuramos el grid de la ventana para que sea responsive
        self.ventana.columnconfigure(0, weight=1)
        self.ventana.rowconfigure(7, weight=1)

        # Frame principal
        frame = LabelFrame(self.ventana, text="Registrar un nuevo Producto", font=('Calibri', 16, 'bold'))
        frame.grid(row=0, column=0, pady=20, padx=20, columnspan=3, sticky='nsew')

        # Configuramos el grid del frame para hacerlo responsive
        frame.columnconfigure(1, weight=1)

        # Nombre
        Label(frame, text="Nombre: ", font=('Calibri', 13)).grid(row=1, column=0, sticky='e')
        self.nombre = Entry(frame, font=('Calibri', 13))
        self.nombre.grid(row=1, column=1, sticky='ew')

        # Precio
        Label(frame, text="Precio: ", font=('Calibri', 13)).grid(row=2, column=0, sticky='e')
        self.precio = Entry(frame, font=('Calibri', 13))
        self.precio.grid(row=2, column=1, sticky='ew')

        # Categoría
        Label(frame, text="Categoría: ", font=('Calibri', 13)).grid(row=3, column=0, sticky='e')  # Nuevo campo
        self.categoria = Entry(frame, font=('Calibri', 13))
        self.categoria.grid(row=3, column=1, sticky='ew')

        # Stock
        Label(frame, text="Stock: ", font=('Calibri', 13)).grid(row=4, column=0, sticky='e')  # Nuevo campo
        self.stock = Entry(frame, font=('Calibri', 13))
        self.stock.grid(row=4, column=1, sticky='ew')

        # Botón para añadir producto con estilo
        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 14, 'bold'))
        self.boton_aniadir = ttk.Button(frame, text="Guardar Producto", command=self.add_producto, style='my.TButton')
        self.boton_aniadir.grid(row=5, columnspan=2, sticky=W + E)

        # Mensaje informativo para el usuario
        self.mensaje = Label(text='', fg='red', font=('Calibri', 13))
        self.mensaje.grid(row=6, column=0, columnspan=2, sticky=W + E)

        # Tabla de productos
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11))
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 13, 'bold'))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        self.tabla = ttk.Treeview(height=10, columns=("precio", "categoria", "stock"), style="mystyle.Treeview")
        self.tabla.grid(row=7, column=0, columnspan=3, sticky='nsew')
        self.tabla.heading('#0', text='Nombre', anchor=CENTER)
        self.tabla.heading('precio', text='Precio', anchor=CENTER)
        self.tabla.heading('categoria', text='Categoría', anchor=CENTER)
        self.tabla.heading('stock', text='Stock', anchor=CENTER)

        # Configuramos las columnas y filas del grid para que la tabla se expanda
        self.ventana.columnconfigure(0, weight=1)
        self.ventana.rowconfigure(7, weight=1)

        # Barra de progreso como nuevo widget gráfico
        self.progreso = Progressbar(self.ventana, orient=HORIZONTAL, length=200, mode='determinate')
        self.progreso.grid(row=8, column=0, pady=10)

        # Botones de Eliminar y Editar con estilo
        self.boton_eliminar = ttk.Button(text='ELIMINAR', command=self.del_producto, style='my.TButton')
        self.boton_eliminar.grid(row=9, column=0, sticky=W + E)
        self.boton_editar = ttk.Button(text='EDITAR', command=self.edit_producto, style='my.TButton')
        self.boton_editar.grid(row=9, column=1, sticky=W + E)

        # Mostrar los productos al iniciar
        self.get_productos()

    def get_productos(self):
        records = self.tabla.get_children()
        for element in records:
            self.tabla.delete(element)

        # Obtener los datos de la base de datos
        productos = session.query(Producto).all()

        # Insertar cada producto en la tabla
        for producto in productos:
            self.tabla.insert('', 'end', text=producto.nombre, values=(producto.precio, producto.categoria, producto.stock))

    def add_producto(self):
        if not self.nombre.get() or not self.precio.get() or not self.categoria.get() or not self.stock.get():
            self.mensaje['text'] = 'Todos los campos son obligatorios'
            return

        nuevo_producto = Producto(
            nombre=self.nombre.get(),
            precio=float(self.precio.get()),
            categoria=self.categoria.get(),
            stock=int(self.stock.get())
        )
        session.add(nuevo_producto)
        session.commit()

        self.mensaje['text'] = f'Producto {self.nombre.get()} guardado con éxito'
        self.get_productos()

    def del_producto(self):
        self.mensaje['text'] = ''
        try:
            producto_seleccionado = self.tabla.item(self.tabla.selection())['text']
        except IndexError:
            self.mensaje['text'] = 'Por favor, seleccione un producto'
            return

        producto = session.query(Producto).filter_by(nombre=producto_seleccionado).first()
        session.delete(producto)
        session.commit()

        self.mensaje['text'] = f'Producto {producto_seleccionado} eliminado con éxito'
        self.get_productos()

    def edit_producto(self):
        # Comprobar si hay un producto seleccionado
        try:
            producto_seleccionado = self.tabla.item(self.tabla.selection())['text']
            producto = session.query(Producto).filter_by(nombre=producto_seleccionado).first()
            VentanaEditarProducto(self, producto)
        except IndexError:
            self.mensaje['text'] = 'Por favor, seleccione un producto para editar'

class VentanaEditarProducto:
    def __init__(self, ventana_principal, producto):
        self.ventana_principal = ventana_principal
        self.producto = producto
        self.ventana_editar = Toplevel()
        self.ventana_editar.title("Editar Producto")

        frame_ep = LabelFrame(self.ventana_editar, text="Editar Producto", font=('Calibri', 16, 'bold'))
        frame_ep.grid(row=0, column=0, pady=20, padx=20, columnspan=2, sticky='nsew')

        Label(frame_ep, text="Nombre: ", font=('Calibri', 13)).grid(row=1, column=0, sticky='e')
        self.input_nombre_nuevo = Entry(frame_ep, font=('Calibri', 13), textvariable=StringVar(self.ventana_editar, value=self.producto.nombre))
        self.input_nombre_nuevo.grid(row=1, column=1, sticky='ew')

        Label(frame_ep, text="Precio: ", font=('Calibri', 13)).grid(row=2, column=0, sticky='e')
        self.input_precio_nuevo = Entry(frame_ep, font=('Calibri', 13), textvariable=StringVar(self.ventana_editar, value=str(self.producto.precio)))
        self.input_precio_nuevo.grid(row=2, column=1, sticky='ew')

        Label(frame_ep, text="Categoría: ", font=('Calibri', 13)).grid(row=3, column=0, sticky='e')
        self.input_categoria_nueva = Entry(frame_ep, font=('Calibri', 13), textvariable=StringVar(self.ventana_editar, value=self.producto.categoria))
        self.input_categoria_nueva.grid(row=3, column=1, sticky='ew')

        Label(frame_ep, text="Stock: ", font=('Calibri', 13)).grid(row=4, column=0, sticky='e')
        self.input_stock_nuevo = Entry(frame_ep, font=('Calibri', 13), textvariable=StringVar(self.ventana_editar, value=str(self.producto.stock)))
        self.input_stock_nuevo.grid(row=4, column=1, sticky='ew')

        self.boton_guardar = ttk.Button(frame_ep, text="Guardar Cambios", command=self.guardar_cambios, style='my.TButton')
        self.boton_guardar.grid(row=5, columnspan=2, sticky=W + E)

    def guardar_cambios(self):
        self.producto.nombre = self.input_nombre_nuevo.get()
        self.producto.precio = float(self.input_precio_nuevo.get())
        self.producto.categoria = self.input_categoria_nueva.get()
        self.producto.stock = int(self.input_stock_nuevo.get())

        session.commit()
        self.ventana_principal.get_productos()
        self.ventana_editar.destroy()

if __name__ == "__main__":
    root = Tk()
    app = VentanaPrincipal(root)
    root.mainloop()
