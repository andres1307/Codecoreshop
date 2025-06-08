from flask import Flask, render_template
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask_sqlalchemy import SQLAlchemy

# ----------------------------
# INICIALIZACIÓN DE LA APLICACIÓN
# ----------------------------
app = Flask(__name__)
app.secret_key = 'Omegafito7217*'

# ----------------------------
# CONFIGURACIÓN DE POSTGRESQL (USANDO TUS CREDENCIALES)
# ----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:codecoreshop@localhost:5432/codecoreshop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ----------------------------
# MODELOS DE LA BASE DE DATOS (MAPEADOS A TUS TABLAS EXISTENTES)
# ----------------------------
class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    estado = db.Column(db.String(20), default='activo')
    fecha_nacimiento = db.Column(db.Date)
    ultima_conexion = db.Column(db.DateTime)

class Genero(db.Model):
    __tablename__ = 'generos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    productos = db.relationship('Producto', backref='genero', lazy=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    imagen = db.Column(db.String(255))
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    referencia = db.Column(db.String(100), unique=True, nullable=False)
    genero_id = db.Column(db.Integer, db.ForeignKey('generos.id'))
    descripcion = db.Column(db.Text)

class Carrito(db.Model):
    __tablename__ = 'carrito'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Integer, default=1)
    usuario = db.relationship('Usuario', backref='carritos')
    producto = db.relationship('Producto')

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha = db.Column(db.DateTime, server_default=db.func.now())
    total = db.Column(db.Numeric(10, 2), nullable=False)
    usuario = db.relationship('Usuario', backref='pedidos')

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    pedido = db.relationship('Pedido', backref='detalles')
    producto = db.relationship('Producto')

# ----------------------------
# CONFIGURACIÓN DE SUBIDA DE ARCHIVOS (EXISTENTE)
# ----------------------------
app.config['UPLOADED_IMAGES_DEST'] = 'static/media'
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

# ----------------------------
# FUNCIONES DE DATOS COMUNES (PARA PASAR DATOS A LAS PLANTILLAS)
# ----------------------------
def get_common_data():
    MenuApp = [
        {"nombre": "Inicio", "url": "index"},
        {"nombre": "Productos", "url": "productos"},
        {"nombre": "Servicios", "url": "servicios"},
        {"nombre": "¿Quienes Somos?", "url": "index#quienes_somos"},
        {"nombre": "Contactanos", "url": "index#contactenos"},
        {"nombre": "Ingresar", "url": "login"}
    ]
    return {
        'datosApp': {
            'titulo': 'CodecoreShop',
            'MenuAppindex': MenuApp,
            'longMenuAppindex': len(MenuApp)
        }
    }

def get_data_app():
    App = [
        {"nombre": "Menu Principal", "url": "dashboard_admin", "icono": "home"},
        {"nombre": "Dashboard", "url": "dashboard_admin", "icono": "chart-line"},
        {
            "nombre": "Gestion Productos",
            "url": "GestionProductos",
            "icono": "box",
            "submodulos": [
                {"nombre": "Agregar Producto", "url": "GestionProductos", "icono": "plus"},
                {"nombre": "Editar Producto", "url": "editar_productos", "icono": "edit"},
                {"nombre": "Eliminar Producto", "url": "eliminar_productos", "icono": "trash"}
            ]
        },
        {"nombre": "Cerrar Sesion", "url": "logout", "icono": "sign-out-alt"}
    ]
    return {
        'titulo': 'CodecoreShop',
        'MenuAppindex': App,
        'longMenuAppindex': len(App)
    }

# ----------------------------
# RUTAS BÁSICAS DE EJEMPLO (Con variables necesarias para plantillas)
# ----------------------------

@app.route('/')
def index():
    return render_template('index.html', **get_common_data())

@app.route('/productos')
def productos():
    productos = Producto.query.all()
    # paso productos como lista de tuplas como tú lo usas en la plantilla productos.html
    lista_productos = []
    for p in productos:
        lista_productos.append((
            p.id,
            p.imagen,
            p.nombre,
            float(p.precio),  # convertir Numeric a float para que se muestre bien en template
            p.referencia,
            p.genero.nombre if p.genero else "",
            p.descripcion
        ))
    # paso datosApp en el mismo dict para que no falle en plantilla
    return render_template('productos.html', productos=lista_productos, **get_common_data())

# Agregadas rutas que usas en los menús para que no falle url_for

@app.route('/servicios')
def servicios():
    return render_template('servicios.html', **get_common_data())

@app.route('/login')
def login():
    return render_template('login.html', **get_common_data())

@app.route('/dashboard_admin')
def dashboard_admin():
    return render_template('dashboard_admin.html', **get_data_app())

@app.route('/GestionProductos')
def GestionProductos():
    return render_template('gestion_productos.html', **get_data_app())

@app.route('/editar_productos')
def editar_productos():
    return render_template('editar_productos.html', **get_data_app())

@app.route('/eliminar_productos')
def eliminar_productos():
    return render_template('eliminar_productos.html', **get_data_app())

@app.route('/logout')
def logout():
    # Aquí va lógica de cerrar sesión si quieres, ahora redirige a index
    return render_template('index.html', **get_common_data())

# ----------------------------
# INICIALIZACIÓN DEL SERVIDOR
# ----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
