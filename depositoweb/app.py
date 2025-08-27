from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os, logging, json, datetime
import functools
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash
from telegram import Bot
from telegram.error import TelegramError


logging.basicConfig(format='%(asctime)s - CRUD - %(levelname)s - %(message)s', level=logging.INFO)





app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)



# -------------- FLASK ----------------
app.secret_key = os.environ["FLASK_SECRET_KEY"] 


#--------------- TELEGRAM ------------
TELEGRAM_BOT_TOKEN = os.getenv('TB_TOKEN') 
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHATID')     



# ------------- SQLALCHEMY -------------

DB_USER = os.environ.get('MARIADB_USER')
DB_PASSWORD = os.environ.get('MARIADB_USER_PASS')
DB_NAME = os.environ.get('MARIADB_DB')
DB_HOST = os.environ.get('MARIADB_SERVER') 

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
print(f"DEBUG_DB: SQLALCHEMY_DATABASE_URI es: {app.config['SQLALCHEMY_DATABASE_URI']}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) 

#----- MODELADO DE LA BASE DE DATOS ---------------

class RegistroDeposito(db.Model):
    __tablename__ = 'registros_deposito'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_cliente = db.Column(db.String(100), nullable=False)
    email_cliente = db.Column(db.String(100), nullable=False)
    telefono_cliente = db.Column(db.String(20), nullable=True)
    tipo_objeto = db.Column(db.String(50), nullable=False)
    nombre_objeto = db.Column(db.Text, nullable=False)
    superficie = db.Column(db.Float, nullable=False)
    precio_calculado = db.Column(db.String(50), nullable=False)
    caja_recomendada = db.Column(db.String(50), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.datetime.now) 

    def __repr__(self):
        return f'<Registro {self.nombre_cliente} - {self.nombre_objeto}>'

# -------- MODELO PARA USUARIOS ADMINISTRADORES ---------------
class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Inicialización bot de telegram
telegram_bot = None
if TELEGRAM_BOT_TOKEN:
    try:
        telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)
        print("Telegram bot inicializado correctamente.")
    except Exception as e:
        print(f"Error al inicializar el bot de Telegram: {e}")
else:
    print("TELEGRAM_BOT_TOKEN no configurado. Las notificaciones por Telegram no funcionarán.")


# ------ DECORADOR PARA RUTAS PROTEGIDAS -------
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

#---------- FUNCIONES AUXILIARES --------

def calcular_precio_deposito(superficie_m2):
    precio_base = 5000
    costo_por_m2 = 6000
    if superficie_m2 <= 0:
        return 0
    precio_calculado = precio_base + (superficie_m2 * costo_por_m2)
    return int(precio_calculado)

def recomendar_caja(superficie_m2):
    if superficie_m2 <= 0.5:
        return "Caja Pequeña (hasta 0.5 m²)"
    elif superficie_m2 <= 1.5:
        return "Caja Mediana (hasta 1.5 m²)"
    elif superficie_m2 <= 3.0:
        return "Caja Grande (hasta 3.0 m²)"
    else:
        return "Contenedor Especial (más de 3.0 m²)"

async def send_telegram_notification(message):
    if not telegram_bot:
        print("No se puede enviar notificación de Telegram: bot no inicializado.")
        return False
    if not TELEGRAM_CHAT_ID:
        print("No se puede enviar notificación de Telegram: TELEGRAM_CHAT_ID no configurado.")
        return False
    
    try:
        await telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")
        print(f"Notificación de Telegram enviada: {message}")
        return True
    except TelegramError as e:
        print(f"Error al enviar notificación de Telegram: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado al enviar notificación de Telegram: {e}")
        return False
    



#------------ RUTAS -----------

@app.route('/')
def index():
    return redirect(url_for('calculadora'))

@app.route('/login',methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = AdminUser.query.filter_by(username=username).first()

        
        if user and user.check_password(password):
            session['logged_in'] = True
            flash('Has iniciado sesión con éxito.', 'success')
            return redirect(url_for('listar_registros'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Has cerrado sesión.','info')
    return redirect(url_for('login'))

@app.route('/calculadora')
def calculadora():
    current_year = datetime.datetime.now().year
    return render_template('calculadora.html',current_year = current_year)

@app.route('/calcular_precio', methods=["POST"])
def calcular_precio():
    try:
        data = request.get_json()
        superficie = float(data['superficie'])

        precio = calcular_precio_deposito(superficie)
        caja_recomendada = recomendar_caja(superficie)
        
        return jsonify({'precio': precio, 'caja_recomendada': caja_recomendada})
    except TypeError:
        return jsonify({'error': 'Formato de datos JSON inválido. Se esperaba un número para "superficie".'}), 400
    except ValueError:
        return jsonify({'error': 'La superficie debe ser un número válido.'}), 400
    except Exception as e:
        print(f"Error en calcular_precio: {e}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/registrar_producto', methods=["POST"])
async def registrar_producto():
    try:
        nombre_cliente = request.form['nombre_cliente']
        email_cliente = request.form['email_cliente']
        telefono_cliente = request.form.get('telefono_cliente')

        tipo_objeto = request.form['tipo_objeto']
        nombre_objeto = request.form['nombre_objeto']
        superficie = float(request.form['superficie'])
        precio = request.form['precio_calculado']
        caja = request.form['caja_recomendada']

        nuevo_registro = RegistroDeposito(
            nombre_cliente=nombre_cliente,
            email_cliente=email_cliente,
            telefono_cliente=telefono_cliente,
            tipo_objeto=tipo_objeto,
            nombre_objeto=nombre_objeto,
            superficie=superficie,
            precio_calculado=precio,
            caja_recomendada=caja
        )

        db.session.add(nuevo_registro)
        db.session.commit()

        # --- Lógica de notificación por Telegram ---
        notification_message = (
            f"<b>📦 Nuevo Registro de Depósito:</b>\n"
            f"👤 Cliente: <b>{nombre_cliente}</b>\n"
            f"📧 Email: {email_cliente}\n"
            f"📞 Teléfono: {telefono_cliente if telefono_cliente else 'N/A'}\n"
            f"🛋️ Objetos: {nombre_objeto}\n"
            f"📐 Superficie: <b>{superficie} m²</b>\n"
            f"💰 Precio Estimado: <b>${precio} ARS</b>\n"
            f"📦 Caja Recomendada: <b>{caja}</b>"
        )
        
        #Se usa await pq send_telegram_notification es async
        await send_telegram_notification(notification_message)

        flash('¡Tu solicitud de depósito ha sido registrada con éxito! Te contactaremos a la brevedad.', 'success')
        return redirect(url_for('calculadora'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar tu solicitud: {e}', 'danger')
        return redirect(url_for('calculadora'))

@app.route('/registros')
@login_required
def listar_registros():
    print("---------------------------------")
    print("Accediendo a /registros")
    print("Contenido de la sesión:", session)
    print("Estado de logged_in:", session.get('logged_in'))
    print("---------------------------------")
    todos_los_registros = RegistroDeposito.query.order_by(RegistroDeposito.fecha_registro.desc()).all()
    return render_template('registros.html', registros=todos_los_registros)

if __name__ == '__main__':
    with app.app_context():
        if not AdminUser.query.filter_by(username='admin').first():
            print("Creando usuario admin por defecto...")
            default_admin = AdminUser(username='admin')
            default_admin.set_password('admin123')
            db.session.add(default_admin)
            db.session.commit()
            print("Usuario 'admin' creado con contraseña 'admin123'.")
        else:
            print("El usuario 'admin' ya existe.")

    app.run(host='0.0.0.0', port=5000)
