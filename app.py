import base64
import datetime
from datetime import datetime, timedelta
import os
import random
import re
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import mysql.connector
import requests
from twilio.rest import Client
import json
from werkzeug.utils import secure_filename

import shutil
from PIL import Image
import io
from rembg import remove

def ejecutar_ia_propia(input_path, output_path, efecto):
    """
    Composición local avanzada con IA (rembg + PIL):
    Elimina el fondo de la mascota y la integra con los accesorios/escenarios 
    según el efecto seleccionado (Verano Caribeño, Bambí Zen, Festival Nocturno, Orgullo Tricolor).
    """
    try:
        print(f"Iniciando composición local para el efecto: {efecto}...")
        
        # 1. Remover fondo con rembg
        with open(input_path, 'rb') as i:
            input_data = i.read()
        
        output_data = remove(input_data)
        mascota_sin_fondo = Image.open(io.BytesIO(output_data)).convert("RGBA")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        fondos_dir = os.path.join(base_dir, 'static', 'fondos')

        efecto_lower = efecto.lower()

        # 2. Selección de fondo según la clave del efecto
        if "verano" in efecto_lower or "playa" in efecto_lower:
            fondo_filename = "fondo_verano.jpg"
        elif "bambi" in efecto_lower or "kimono" in efecto_lower or "zen" in efecto_lower:
            fondo_filename = "fondo_zen.jpg"
        elif "festival" in efecto_lower or "cerezo" in efecto_lower:
            fondo_filename = "fondo_festival.jpg"
        elif "mexico" in efecto_lower or "camiseta" in efecto_lower or "tricolor" in efecto_lower:
            fondo_filename = "fondo_tricolor.jpg"
        else:
            fondo_filename = "fondo_verano.jpg"

        fondo_path = os.path.join(fondos_dir, fondo_filename)

        # Si no se encuentra el archivo de fondo, se genera un lienzo blanco sólido para evitar fondo negro
        if not os.path.exists(fondo_path):
            print(f"⚠️ Fondo no encontrado en {fondo_path}. Usando lienzo blanco por defecto.")
            lienzo = Image.new("RGBA", (800, 800), (255, 255, 255, 255))
        else:
            lienzo = Image.open(fondo_path).convert("RGBA")
            lienzo = lienzo.resize((800, 800), Image.Resampling.LANCZOS)

        # 3. Escalar a la mascota proporcionalmente para que encaje bien en el escenario
        max_size = 500
        ratio = float(max_size) / max(mascota_sin_fondo.width, mascota_sin_fondo.height)
        new_size = (int(mascota_sin_fondo.width * ratio), int(mascota_sin_fondo.height * ratio))
        mascota_resaltada = mascota_sin_fondo.resize(new_size, Image.Resampling.LANCZOS)

        # 4. Ajuste de posición (centrado horizontalmente en la parte inferior sobre el flotador o vestuario)
        pos_x = (lienzo.width - mascota_resaltada.width) // 2
        pos_y = lienzo.height - mascota_resaltada.height - 50

        # 5. Fusionar la mascota sobre el lienzo usando la capa Alpha como máscara
        lienzo.paste(mascota_resaltada, (pos_x, pos_y), mascota_resaltada)

        # 6. Convertir a RGB y guardar como JPEG limpio
        final_img = lienzo.convert("RGB")
        final_img.save(output_path, "JPEG", quality=95)
        return True

    except Exception as e:
        print(f"--- ERROR EN COMPOSICIÓN DE EFECTO: {str(e)} ---")
        # En caso de falla grave, crear una copia limpia convertida a RGB
        try:
            img_backup = Image.open(input_path).convert("RGB")
            img_backup.save(output_path, "JPEG", quality=90)
        except Exception:
            shutil.copyfile(input_path, output_path)
        return False

        

# 1. Instancia de Flask y soporte CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

GOOGLE_CLIENT_ID = "144324961012-sv6ggpbi9gn0sc3f6jap6n9ckkfhcc5q.apps.googleusercontent.com"

# -------------------------------------------------------------------
# CONFIGURACIÓN DE BASE DE DATOS (LOCAL XAMPP)
# -------------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "kova_db"),
    "charset": "utf8mb4",
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# --- Configuración de Flask-Mail (Gmail) ---
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USERNAME"] = "kevinurielremigioelizalde@gmail.com"
app.config["MAIL_PASSWORD"] = "mwfr xqhn nfmm cymk"
app.config["MAIL_DEFAULT_SENDER"] = ("KOVA", "kevinurielremigioelizalde@gmail.com")
app.config["MAIL_ASCII_ATTACHMENTS"] = False
app.config["MAIL_CHARSET"] = "utf-8"

mail = Mail(app)

# --- Configuración de Carpetas de Carga ---
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
GENERADOS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'generados')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERADOS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERADOS_FOLDER'] = GENERADOS_FOLDER


# -------------------------------------------------------------------
# RUTAS DE VISTAS DE PÁGINAS (HTML)
# -------------------------------------------------------------------

@app.route('/')
def home():
    return render_template('pagina_central.html')

@app.route('/login')
def login_view():
    return render_template('index.html')

@app.route('/usuarios')
def usuarios():
    return render_template('kova_usuarios.html')

@app.route('/prestador')
def prestador():
    return render_template('prestador_servicios.html')

@app.route('/vendedor')
def vendedor():
    return render_template('vendedor_productos.html')

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html')

@app.route('/galeria')
def galeria():
    return render_template('galeria.html')

@app.route('/mapa')
def mapa():
    return render_template('mapa.html')

@app.route('/suscripciones')
def suscripciones():
    return render_template('suscripciones.html')


# -------------------------------------------------------------------
# ENDPOINTS DE AUTENTICACIÓN Y USUARIOS
# -------------------------------------------------------------------

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def api_login():
    if request.method == 'OPTIONS':
        return "", 200

    try:
        data = request.get_json() or {}
        correo = data.get('correo_electronico', '').strip()
        contrasena = data.get('contrasena', '').strip()

        if not correo or not contrasena:
            return jsonify({"success": False, "message": "Por favor ingresa correo y contraseña."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT id_usuario, nombre_completo, correo_electronico, telefono, tipo_usuario 
            FROM usuarios 
            WHERE correo_electronico = %s AND contrasena = %s
        """
        cursor.execute(query, (correo, contrasena))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if usuario:
            tipo_usuario = str(usuario.get('tipo_usuario', 'Titular de mascota')).strip()
            return jsonify({
                "success": True,
                "status": "success",
                "message": f"¡Bienvenido de nuevo, {usuario['nombre_completo']}!",
                "user": usuario,
                "tipo_usuario": tipo_usuario
            }), 200
        else:
            return jsonify({"success": False, "message": "Correo o contraseña incorrectos."}), 401

    except Exception as e:
        print("Error en /api/login:", str(e))
        return jsonify({"success": False, "message": f"Error en el servidor: {str(e)}"}), 500


@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return "", 200

    try:
        data = request.get_json() or {}
        nombre = data.get('nombre_completo', '').strip()
        correo = data.get('correo_electronico', '').strip()
        telefono = data.get('telefono', '').strip()
        contrasena = data.get('contrasena', '').strip()
        tipo_usuario = data.get('tipo_usuario', 'Titular de mascota').strip()

        if not nombre or not correo or not contrasena:
            return jsonify({"success": False, "message": "Por favor completa todos los campos obligatorios."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo_electronico = %s", (correo,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "El correo electrónico ya está registrado."}), 400

        query = """
            INSERT INTO usuarios (nombre_completo, correo_electronico, telefono, contrasena, tipo_usuario)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, correo, telefono, contrasena, tipo_usuario))
        conn.commit()
        
        nuevo_id = cursor.lastrowid
        cursor.execute("SELECT id_usuario, nombre_completo, correo_electronico, telefono, tipo_usuario FROM usuarios WHERE id_usuario = %s", (nuevo_id,))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "status": "success",
            "message": "¡Cuenta creada con éxito!",
            "user": usuario,
            "tipo_usuario": tipo_usuario
        }), 200

    except Exception as e:
        print("Error en /api/register:", str(e))
        return jsonify({"success": False, "message": f"Error en el servidor: {str(e)}"}), 500


# -------------------------------------------------------------------
# ENDPOINTS DE RECUPERACIÓN DE CONTRASEÑA
# -------------------------------------------------------------------

@app.route('/api/request-reset-code', methods=['POST', 'OPTIONS'])
def request_reset_code():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json() or {}
        correo = data.get('correo_electronico', '').strip()

        if not correo:
            return jsonify({"success": False, "message": "Por favor ingresa tu correo electrónico."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo_electronico = %s", (correo,))
        usuario = cursor.fetchone()

        if not usuario:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "El correo electrónico no está registrado."}), 404

        # Generar código numérico de 6 dígitos
        codigo = str(random.randint(100000, 999999))
        expiracion = datetime.now() + timedelta(minutes=15)

        cursor.execute(
            "UPDATE usuarios SET reset_code = %s, reset_code_expires = %s WHERE correo_electronico = %s",
            (codigo, expiracion, correo)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Enviar correo electrónico vía Flask-Mail
        msg = Message()
        msg.subject = "Código de Verificación - KOVA"
        msg.recipients = [correo]
        msg.body = f"Hola,\n\nTu código de verificación para restablecer tu contraseña en KOVA es: {codigo}\n\nEste código expira en 15 minutos."
        mail.send(msg)

        return jsonify({"success": True, "message": "Código de verificación enviado a tu correo."}), 200

    except Exception as e:
        print("Error en /api/request-reset-code:", str(e))
        return jsonify({"success": False, "message": f"Error al enviar el correo: {str(e)}"}), 500


@app.route('/api/verify-reset-code', methods=['POST', 'OPTIONS'])
def verify_reset_code():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json() or {}
        correo = data.get('correo_electronico', '').strip()
        codigo = data.get('codigo', '').strip()
        nueva_contrasena = data.get('nueva_contrasena', '').strip()

        if not correo or not codigo or not nueva_contrasena:
            return jsonify({"success": False, "message": "Por favor completa todos los campos."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT reset_code, reset_code_expires FROM usuarios WHERE correo_electronico = %s",
            (correo,)
        )
        usuario = cursor.fetchone()

        if not usuario or usuario['reset_code'] != codigo:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "El código de verificación es incorrecto."}), 400

        if datetime.now() > usuario['reset_code_expires']:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "El código ha expirado. Solicita uno nuevo."}), 400

        # Actualizar contraseña y limpiar token de recuperación
        cursor.execute(
            "UPDATE usuarios SET contrasena = %s, reset_code = NULL, reset_code_expires = NULL WHERE correo_electronico = %s",
            (nueva_contrasena, correo)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "¡Contraseña actualizada exitosamente!"}), 200

    except Exception as e:
        print("Error en /api/verify-reset-code:", str(e))
        return jsonify({"success": False, "message": f"Error en el servidor: {str(e)}"}), 500

# -------------------------------------------------------------------
# ENDPOINTS DE REGISTRO Y GESTIÓN DE MASCOTAS
# -------------------------------------------------------------------

@app.route('/api/registrar_mascota', methods=['POST', 'OPTIONS'])
def registrar_mascota():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json() or {}
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO registro_mascota 
            (id_usuario, nombre_mascota, fecha_nacimiento, raza, color, peso_kg, imagen, token_nfc, nom_tutor, 
             tel_cont_1, tel_cont_2, tel_cont_3, tel_cont_4, tel_cont_5, descripcion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get('usuario_id'), data.get('nombre_mascota'), data.get('fecha_nacimiento') or None,
            data.get('raza', ''), data.get('color'), data.get('peso_kg') or None,
            data.get('imagen', ''), data.get('token_nfc', ''), data.get('nom_tutor', ''),
            data.get('tel_cont_1', ''), data.get('tel_cont_2', ''), data.get('tel_cont_3', ''),
            data.get('tel_cont_4', ''), data.get('tel_cont_5', ''), data.get('descripcion', '')
        )
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Mascota registrada exitosamente."}), 200
    except Exception as e:
        print("Error en /api/registrar_mascota:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/mascotas/<int:usuario_id>', methods=['GET'])
def obtener_mascotas_usuario(usuario_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM registro_mascota WHERE id_usuario = %s ORDER BY id_mascota DESC", (usuario_id,))
        mascotas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "mascotas": mascotas}), 200
    except Exception as e:
        print("Error en /api/mascotas:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/editar_mascota/<int:id_mascota>', methods=['PUT', 'OPTIONS'])
def editar_mascota(id_mascota):
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json() or {}
        conn = get_db_connection()
        cursor = conn.cursor()

        imagen_nueva = data.get('imagen', '')
        if imagen_nueva:
            query = """
                UPDATE registro_mascota 
                SET nombre_mascota = %s, fecha_nacimiento = %s, color = %s, peso_kg = %s, 
                    imagen = %s, token_nfc = %s, nom_tutor = %s, tel_cont_1 = %s, 
                    tel_cont_2 = %s, tel_cont_3 = %s, tel_cont_4 = %s, tel_cont_5 = %s, descripcion = %s
                WHERE id_mascota = %s
            """
            values = (
                data.get('nombre_mascota'), data.get('fecha_nacimiento') or None,
                data.get('color'), data.get('peso_kg') or None,
                imagen_nueva, data.get('token_nfc', ''), data.get('nom_tutor', ''),
                data.get('tel_cont_1', ''), data.get('tel_cont_2', ''), data.get('tel_cont_3', ''),
                data.get('tel_cont_4', ''), data.get('tel_cont_5', ''), data.get('descripcion', ''),
                id_mascota
            )
        else:
            query = """
                UPDATE registro_mascota 
                SET nombre_mascota = %s, fecha_nacimiento = %s, color = %s, peso_kg = %s, 
                    token_nfc = %s, nom_tutor = %s, tel_cont_1 = %s, 
                    tel_cont_2 = %s, tel_cont_3 = %s, tel_cont_4 = %s, tel_cont_5 = %s, descripcion = %s
                WHERE id_mascota = %s
            """
            values = (
                data.get('nombre_mascota'), data.get('fecha_nacimiento') or None,
                data.get('color'), data.get('peso_kg') or None,
                data.get('token_nfc', ''), data.get('nom_tutor', ''),
                data.get('tel_cont_1', ''), data.get('tel_cont_2', ''), data.get('tel_cont_3', ''),
                data.get('tel_cont_4', ''), data.get('tel_cont_5', ''), data.get('descripcion', ''),
                id_mascota
            )

        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Datos de la mascota actualizados exitosamente."}), 200

    except Exception as e:
        print("Error en /api/editar_mascota:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

# -------------------------------------------------------------------
# ENDPOINTS DE PRODUCTOS (VENDEDOR Y CATÁLOGO)
# -------------------------------------------------------------------

@app.route('/api/registrar_producto', methods=['POST'])
def registrar_producto():
    try:
        id_vendedor = request.form.get('id_vendedor')
        nombre = request.form.get('nombre_producto')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio')
        cantidad = request.form.get('cantidad')
        nombre_proveedor = request.form.get('nombre_proveedor')
        contacto_proveedor = request.form.get('contacto_proveedor')

        imgs = []
        for i in range(1, 6):
            file = request.files.get(f'imagen_{i}')
            if file and file.filename != '':
                filename = f"{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                imgs.append(filename)
            else:
                imgs.append(None)

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO productos_vendedor 
            (id_vendedor, nombre_producto, descripcion, precio, cantidad, imagen_1, imagen_2, imagen_3, imagen_4, imagen_5, nombre_proveedor, contacto_proveedor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            id_vendedor, nombre, descripcion, precio, cantidad, 
            imgs[0], imgs[1], imgs[2], imgs[3], imgs[4], 
            nombre_proveedor, contacto_proveedor
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Producto registrado correctamente"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos_vendedor ORDER BY fecha_registro DESC")
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "productos": productos, "data": productos}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/productos_vendedor/<int:id_vendedor>', methods=['GET'])
def obtener_productos_vendedor(id_vendedor):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos_vendedor WHERE id_vendedor = %s ORDER BY fecha_registro DESC", (id_vendedor,))
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "data": productos, "productos": productos}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/actualizar_producto/<int:id_producto>', methods=['POST'])
def actualizar_producto(id_producto):
    try:
        nombre = request.form.get('nombre_producto')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio')
        cantidad = request.form.get('cantidad')
        nombre_proveedor = request.form.get('nombre_proveedor')
        contacto_proveedor = request.form.get('contacto_proveedor')

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            UPDATE productos_vendedor 
            SET nombre_producto = %s, descripcion = %s, precio = %s, cantidad = %s, nombre_proveedor = %s, contacto_proveedor = %s
            WHERE id_producto = %s
        """
        cursor.execute(query, (nombre, descripcion, precio, cantidad, nombre_proveedor, contacto_proveedor, id_producto))

        for i in range(1, 6):
            file = request.files.get(f'imagen_{i}')
            if file and file.filename != '':
                filename = f"{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                cursor.execute(f"UPDATE productos_vendedor SET imagen_{i} = %s WHERE id_producto = %s", (filename, id_producto))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Producto actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/eliminar_producto/<int:id_producto>', methods=['DELETE', 'OPTIONS'])
def eliminar_producto(id_producto):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos_vendedor WHERE id_producto = %s", (id_producto,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Producto eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# -------------------------------------------------------------------
# ENDPOINTS DE SERVICIOS (PRESTADOR Y CATÁLOGO)
# -------------------------------------------------------------------

@app.route('/api/crear_servicio', methods=['POST'])
def crear_servicio():
    try:
        id_usuario = request.form.get('id_usuario')
        tipo_servicio = request.form.get('tipo_servicio')
        nombre_prestador = request.form.get('nombre_prestador')
        edad = request.form.get('edad')
        descripcion = request.form.get('descripcion')
        dias_servicio = request.form.get('dias_servicio')
        precio = request.form.get('precio')
        lugar_servicio = request.form.get('lugar_servicio')
        ubicacion = request.form.get('ubicacion', '')
        contacto = request.form.get('contacto')

        rutas_imagenes = []
        for img_key in ['imagen1', 'imagen2']:
            if img_key in request.files:
                file = request.files[img_key]
                if file and file.filename != '':
                    filename = secure_filename(f"{int(datetime.now().timestamp())}_{file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    rutas_imagenes.append(filename)
                else:
                    rutas_imagenes.append(None)
            else:
                rutas_imagenes.append(None)

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """INSERT INTO servicios (id_usuario, tipo_servicio, nombre_prestador, edad, descripcion, dias_servicio, precio, lugar_servicio, ubicacion, contacto, imagen1, imagen2) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        valores = (id_usuario, tipo_servicio, nombre_prestador, edad, descripcion, dias_servicio, precio, lugar_servicio, ubicacion, contacto, rutas_imagenes[0], rutas_imagenes[1])
        
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "status": "success", "message": "Servicio registrado correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "status": "error", "message": str(e)}), 500


@app.route('/api/mis_servicios/<int:id_usuario>', methods=['GET'])
def mis_servicios(id_usuario):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM servicios WHERE id_usuario = %s ORDER BY fecha_registro DESC", (id_usuario,))
        servicios = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "data": servicios, "servicios": servicios}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/editar_servicio/<int:id_servicio>', methods=['POST', 'OPTIONS'])
def editar_servicio(id_servicio):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        tipo_servicio = request.form.get('tipo_servicio')
        nombre_prestador = request.form.get('nombre_prestador')
        edad = request.form.get('edad')
        descripcion = request.form.get('descripcion')
        dias_servicio = request.form.get('dias_servicio')
        precio = request.form.get('precio')
        lugar_servicio = request.form.get('lugar_servicio')
        ubicacion = request.form.get('ubicacion', '')
        contacto = request.form.get('contacto')

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """UPDATE servicios 
                   SET tipo_servicio=%s, nombre_prestador=%s, edad=%s, descripcion=%s, 
                       dias_servicio=%s, precio=%s, lugar_servicio=%s, ubicacion=%s, contacto=%s 
                   WHERE id_servicio=%s"""
        cursor.execute(query, (tipo_servicio, nombre_prestador, edad, descripcion, dias_servicio, precio, lugar_servicio, ubicacion, contacto, id_servicio))

        # Procesar actualización opcional de imágenes
        for i, col in [(1, 'imagen1'), (2, 'imagen2')]:
            file = request.files.get(f'imagen{i}')
            if file and file.filename != '':
                filename = secure_filename(f"{int(datetime.now().timestamp())}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                cursor.execute(f"UPDATE servicios SET {col} = %s WHERE id_servicio = %s", (filename, id_servicio))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "status": "success", "message": "Servicio actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "status": "error", "message": str(e)}), 500


@app.route('/api/catalogo_servicios', methods=['GET'])
def catalogo_servicios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM servicios ORDER BY fecha_registro DESC")
        servicios = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "data": servicios, "servicios": servicios}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/eliminar_servicio/<int:id_servicio>', methods=['DELETE', 'OPTIONS'])
def eliminar_servicio(id_servicio):
    if request.method == 'OPTIONS':
        return '', 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM servicios WHERE id_servicio = %s", (id_servicio,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Servicio eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



# -------------------------------------------------------------------
# ENDPOINTS DE GALERÍA Y PROCESAMIENTO DE EFECTOS CON IA
# -------------------------------------------------------------------

@app.route('/api/subir_y_procesar_ia', methods=['POST', 'OPTIONS'])
def subir_y_procesar_ia():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        id_mascota = request.form.get('id_mascota')
        efecto = request.form.get('efecto', 'playa_verano')
        descripcion = request.form.get('descripcion', '')

        if 'imagen' not in request.files:
            return jsonify({"status": "error", "message": "No se adjuntó ningún archivo de imagen o video."}), 400

        file = request.files['imagen']
        if file.filename == '':
            return jsonify({"status": "error", "message": "Nombre de archivo no válido."}), 400

        filename_original = secure_filename(f"orig_{int(datetime.now().timestamp())}_{file.filename}")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_original)
        file.save(input_path)

        ext = os.path.splitext(file.filename)[1].lower()
        tipo_archivo = 'video' if ext in ['.mp4', '.avi', '.mov', '.webm'] else 'imagen'

        filename_generado = f"ia_{efecto}_{id_mascota}_{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
        output_path = os.path.join(app.config['GENERADOS_FOLDER'], filename_generado)

        if tipo_archivo == 'video':
            shutil.copyfile(input_path, output_path)
        else:
            ejecutar_ia_propia(input_path, output_path, efecto)

        # INSERT en la tabla correcta: galeria_ia
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO galeria_ia (id_mascota, tipo_archivo, nombre_archivo, titulo_efecto, descripcion_efecto)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (id_mascota, tipo_archivo, filename_generado, efecto, descripcion))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Archivo procesado y guardado correctamente.",
            "nombre_archivo": filename_generado
        }), 200

    except Exception as e:
        print("Error en /api/subir_y_procesar_ia:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/galeria/<int:id_mascota>', methods=['GET'])
def obtener_galeria_mascota(id_mascota):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # SELECT desde la tabla correcta: galeria_ia
        cursor.execute("""
            SELECT id_galeria, id_mascota, tipo_archivo, nombre_archivo, titulo_efecto, descripcion_efecto, fecha_creacion 
            FROM galeria_ia 
            WHERE id_mascota = %s 
            ORDER BY fecha_creacion DESC
        """, (id_mascota,))
        galeria = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "galeria": galeria}), 200
    except Exception as e:
        print("Error en /api/galeria:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/actualizar_foto_perfil_ia', methods=['POST', 'OPTIONS'])
def actualizar_foto_perfil_ia():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json() or {}
        id_mascota = data.get('id_mascota')
        nombre_archivo = data.get('nombre_archivo')

        if not id_mascota or not nombre_archivo:
            return jsonify({"status": "error", "message": "Datos incompletos."}), 400

        # Construir la URL estática para la foto de perfil del expediente
        url_foto = f"/static/generados/{nombre_archivo}"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE registro_mascota SET imagen = %s WHERE id_mascota = %s", (url_foto, id_mascota))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Foto de perfil actualizada exitosamente."}), 200
    except Exception as e:
        print("Error en /api/actualizar_foto_perfil_ia:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


# -------------------------------------------------------------------
# ENDPOINTS DE HISTORIAL CLÍNICO
# -------------------------------------------------------------------

@app.route('/actualizar_historial', methods=['POST', 'OPTIONS'])
def actualizar_historial():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        id_mascota = request.form.get('id_mascota')
        nombre_mascota = request.form.get('nombre_mascota', '')
        sexo = request.form.get('sexo', '')
        fecha_nacimiento = request.form.get('fecha_nacimiento') or None
        peso = request.form.get('peso') or None
        raza = request.form.get('raza', '')
        color = request.form.get('color', '')
        esterilizado = request.form.get('esterilizado', '')
        senas_particulares = request.form.get('senas_particulares', '')
        
        nombre_tutor = request.form.get('nombre_tutor', '')
        telefono_1 = request.form.get('telefono_1', '')
        telefono_2 = request.form.get('telefono_2', '')
        email_tutor = request.form.get('email_tutor', '')
        direccion = request.form.get('direccion', '')

        actividad_medica = request.form.get('actividad_medica', '')
        subopcion_medica = request.form.get('subopcion_medica', '')

        # Guardar los campos dinámicos específicos del formulario en formato JSON
        detalles_dict = {}
        for key in request.form.keys():
            if key not in ['id_mascota', 'nombre_mascota', 'sexo', 'fecha_nacimiento', 'peso', 'raza', 'color', 
                            'esterilizado', 'senas_particulares', 'nombre_tutor', 'telefono_1', 'telefono_2', 
                            'email_tutor', 'direccion', 'actividad_medica', 'subopcion_medica']:
                detalles_dict[key] = request.form.get(key)
        
        detalles_json = json.dumps(detalles_dict, ensure_ascii=False)

        # Procesar archivo adjunto si existe
        filename_adjunto = None
        if 'consulta_imagen' in request.files:
            file = request.files['consulta_imagen']
            if file and file.filename != '':
                filename_adjunto = f"hist_{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename_adjunto)
                file.save(filepath)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertar registro en la tabla de historial clínico
        query = """
            INSERT INTO historial_clinico 
            (id_mascota, nombre_mascota, sexo, fecha_nacimiento, peso, raza, color, esterilizado, senas_particulares,
             nombre_tutor, telefono_1, telefono_2, email_tutor, direccion, actividad_medica, subopcion_medica, 
             detalles_formulario, consulta_imagen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            id_mascota, nombre_mascota, sexo, fecha_nacimiento, peso, raza, color, esterilizado, senas_particulares,
            nombre_tutor, telefono_1, telefono_2, email_tutor, direccion, actividad_medica, subopcion_medica,
            detalles_json, filename_adjunto
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Historial clínico actualizado correctamente."}), 200

    except Exception as e:
        print("Error en /actualizar_historial:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/obtener_historial/<int:id_mascota>', methods=['GET'])
def obtener_historial(id_mascota):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM historial_clinico WHERE id_mascota = %s ORDER BY consulta_fecha DESC", (id_mascota,))
        historial = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "data": historial}), 200
    except Exception as e:
        print("Error en /obtener_historial:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

    

# -------------------------------------------------------------------
# SERVIR ARCHIVOS ESTÁTICOS Y SUBIDOS
# -------------------------------------------------------------------

@app.route('/static/uploads/<filename>')
def servir_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# -------------------------------------------------------------------
# ENDPOINT DE AUTENTICACIÓN CON GOOGLE
# -------------------------------------------------------------------

@app.route('/api/google_login', methods=['POST', 'OPTIONS'])
def google_login():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json() or {}
        token = data.get('credential')

        if not token:
            return jsonify({"success": False, "message": "Token de Google no proporcionado."}), 400

        # Verificar el token enviado por la API oficial de Google
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), GOOGLE_CLIENT_ID
        )

        email = idinfo.get('email')
        nombre = idinfo.get('name', 'Usuario Google')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_usuario, nombre_completo, correo_electronico, telefono, tipo_usuario FROM usuarios WHERE correo_electronico = %s", (email,))
        usuario = cursor.fetchone()

        # Si el usuario no existe en la BD, lo registramos automáticamente como Titular de mascota
        if not usuario:
            cursor.execute(
                "INSERT INTO usuarios (nombre_completo, correo_electronico, tipo_usuario) VALUES (%s, %s, %s)",
                (nombre, email, 'Titular de mascota')
            )
            conn.commit()
            cursor.execute("SELECT id_usuario, nombre_completo, correo_electronico, telefono, tipo_usuario FROM usuarios WHERE correo_electronico = %s", (email,))
            usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        tipo_usuario = str(usuario.get('tipo_usuario', 'Titular de mascota')).strip()

        return jsonify({
            "success": True,
            "status": "success",
            "message": f"¡Bienvenido, {usuario['nombre_completo']}!",
            "user": usuario,
            "tipo_usuario": tipo_usuario
        }), 200

    except Exception as e:
        print("Error en /api/google_login:", str(e))
        return jsonify({"success": False, "message": f"Error al autenticar con Google: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)