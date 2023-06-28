# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "danny22"
app.config['MYSQL_DB'] = "bdmedicos"
app.secret_key = 'mysecretkey'
mysql = MySQL(app)


def get_cursor():
    return mysql.connection.cursor()


@app.route('/')
def index():
    return render_template('login.html')
    
@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/login', methods=['POST'])
def login():
    rfc = request.form['rfc']
    password = request.form['password']
    cursor = get_cursor()
    query = 'SELECT RFC FROM usuarios WHERE RFC = %s AND password = %s'
    cursor.execute(query, (rfc, password))
    resultado = cursor.fetchone()
    if resultado is not None:
        return redirect(url_for('menu'))
    else:
        flash('RFC o contraseña incorrectos')
        return redirect(url_for('index'))





# @app.route('/registroExpediente', methods=['POST', 'GET'])
# def registroExpediente():
#     if request.method == 'POST':
        


# ...

# ...

@app.route('/administracionMedicos', methods=['POST', 'GET'])
def administracionMedicos():
    if request.method == 'POST':
        rfc = request.form.get('rfc')
        nombre = request.form.get('nombre')
        cedula = request.form.get('cedula')
        correo = request.form.get('correo')
        password = request.form.get('password')
        rol = request.form.get('rol')

        if not all([rfc, nombre, cedula, correo, password, rol]):
            error_message = "Por favor, completa todos los campos"
            return render_template('administracionMedicos.html', error=error_message)

        if rol == 'medicoadmin':
            rol = 'Médico Admin'
        elif rol == 'medico':
            rol = 'Médico'

        cursor = get_cursor()
        query = 'INSERT INTO usuarios (RFC, NombreCompleto, CedulaProfesional, correo, password, rol) ' \
                'VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (rfc, nombre, cedula, correo, password, rol))
        mysql.connection.commit()

        return redirect(url_for('menu'))

    return render_template('administracionMedicos.html')

@app.route('/registroEXP', methods=['POST', 'GET'])
def registroEXP():
    if request.method == 'POST':
        medico = request.form.get('medicoAtiende')
        nombre = request.form.get('nombrePaciente')
        fecha = request.form.get('fechanacimiento')
        enfermedades = request.form.get('enfermedades')
        alergias = request.form.get('alergias')
        antecedentes = request.form.get('antecedentes')

        cursor = get_cursor()
        query = 'INSERT INTO expedientes (MedicoAtendedor, NombreCompleto, FechaNacimiento, EnfermedadesCronicas, Alergias, AntecedentesFamiliares) ' \
                'VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (medico, nombre, fecha, enfermedades, alergias, antecedentes))
        mysql.connection.commit()

        flash('Expediente guardado exitosamente.')
        return redirect(url_for('menu'))

    return render_template('registroEXP.html')


@app.route('/Actualizar')
def Actualizar():
    return render_template('Actualizar.html')

@app.route('/citaExploracion')
def citaExploracion():
    return render_template('citaExploracion.html')

@app.route('/consultarCitas')
def consultarCitas():
    return render_template('consultarCitas.html')

@app.route('/mostrarRG')
def mostrarRG():
    return render_template('mostrarRG.html')

# ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

