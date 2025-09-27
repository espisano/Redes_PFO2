import sqlite3
from flask import Flask, request, jsonify, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash


DATABASE = 'usuarios.db'
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contrasena_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()



# ENDPOINTS

@app.route('/registro', methods=['POST'])
def registro_usuario():
    data = request.get_json()

    if not data or 'usuario' not in data or 'contrasena' not in data:
        return jsonify({"mensaje": "Datos incompletos. Se requieren 'usuario' y 'contrasena'."}), 400

    username = data['usuario']
    password = data['contrasena']

    
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO usuarios (usuario, contrasena_hash) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        conn.close()
        return jsonify({"mensaje": f"Usuario '{username}' registrado exitosamente."}), 201

    except sqlite3.IntegrityError:
        return jsonify({"mensaje": "Error: El usuario ya existe."}), 409
    except Exception as e:
        return jsonify({"mensaje": f"Error interno del servidor: {e}"}), 500
    
    
@app.route('/login', methods=['POST'])
def inicio_sesion():
    data = request.get_json()

    if not data or 'usuario' not in data or 'contrasena' not in data:
        return jsonify({"mensaje": "Datos incompletos. Se requieren 'usuario' y 'contrasena'."}), 400

    username = data['usuario']
    password = data['contrasena']
   
    conn = get_db_connection()
    user = conn.execute(
        "SELECT contrasena_hash FROM usuarios WHERE usuario = ?", (username,)
    ).fetchone()
    conn.close()

    if user is None:
        return jsonify({"mensaje": "Error: Usuario o contrasena incorrectos."}), 401

    hashed_password = user['contrasena_hash']

    if check_password_hash(hashed_password, password):
        return jsonify({"mensaje": f"Inicio de sesion exitoso! Bienvenido, {username}."}), 200
    else:
        return jsonify({"mensaje": "Error: Usuario o contrasena incorrectos."}), 401
    

@app.route('/tareas', methods=['GET'])
def mostrar_tareas():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Bienvenida</title></head>
    <body>
        <h1>Bienvenido, Welcome, Bem-vindo</h1>

    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '__main__':
    print("Iniciando el servidor en http://127.0.0.1:5000")
    app.run(debug=True)