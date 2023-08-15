from flask import Flask, render_template, request, redirect, url_for,flash, session, jsonify
from flask_mysqldb import MySQL
from functools import wraps
from flask_bcrypt import Bcrypt




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


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        if 'RFC' not in session:
            # Redirigir al inicio de sesión si no ha iniciado sesión
            flash('Debe iniciar sesión para acceder a esta página.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
    
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



@app.route('/administracionMedicos', methods=['POST', 'GET'])
# @login_required
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



@app.route('/register')
def register():
    return render_template('registroEXP.html')


@app.route('/registroEXP', methods=['POST'])
def registroEXP():
    if request.method == 'POST':
        vmedico = request.form['medicoAtiende']
        vnombre = request.form['nombrePaciente']
        vfecha = request.form['fechanacimiento']
        venfermedades = request.form['enfermedades']
        valergias = request.form['alergias']
        vantecedentes = request.form['antecedentes']
        
        CS = mysql.connection.cursor()
        
        # Insertar el perfil con el ID de usuario correspondiente
        CS.execute('INSERT INTO pacientes(MedicoAtendedor, NombreCompleto, FechaNacimiento, EnfermedadesCronicas, Alergias, AntecedentesFamiliares) VALUES (%s, %s, %s, %s, %s,%s)', (vmedico, vnombre,vfecha,venfermedades, valergias, vantecedentes))
        
        mysql.connection.commit()
        flash('Registro exitosamente!')    
        return redirect(url_for('registroEXP'))
    
        


@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    cursor = get_cursor()
    user = None

    if request.method == 'POST':
        rfc = request.form.get('rfc')
        
        # Buscar en la base de datos usando una consulta SQL SELECT
        query = 'SELECT NombreCompleto FROM usuarios WHERE RFC = %s'
        cursor.execute(query, (rfc,))
        result = cursor.fetchone()

        if result:
            user = {
                "RFC": rfc,
                "NombreCompleto": result[0]  # Obteniendo el primer elemento ya que solo estamos solicitando un campo
            }
        else:
            flash('Usuario no encontrado!')

    return render_template('Buscar.html', user=user)








@app.route('/actualizar', methods=['POST'])
def actualizar_registro():
    cursor = get_cursor()

    # Recoger datos del formulario
    rfc = request.form.get('rfc')
    nombre = request.form.get('nombre')
    cedula = request.form.get('cedula')
    correo = request.form.get('correo')
    password = request.form.get('password')
    rol = request.form.get('rol')

    # Actualizar el registro en la base de datos
    query = '''
        UPDATE usuarios
        SET nombre = %s, CedulaProfesional = %s, correo = %s, password = %s, rol = %s
        WHERE RFC = %s
    '''
    cursor.execute(query, (nombre, cedula, correo, password, rol, rfc))
    mysql.connection.commit()

    flash('Registro actualizado exitosamente!')
    return redirect(url_for('buscar'))




# @app.route('/citaExploracion')
# def citaExploracion():
#     return render_template('citaExploracion.html')

@app.route('/citaExploracion', methods=['GET', 'POST'])
def citaExploracion():
    if request.method == 'POST':
        # Obtener los datos del formulario de exploración
        fecha = request.form['fecha']
        peso = request.form['peso']
        altura = request.form['altura']
        temperatura = request.form['temperatura']
        latidos = request.form['latidos']
        saturacion = request.form['saturacion']
        glucosa = request.form['glucosa']
        paciente_id = request.form['paciente']  # Obtener el ID del paciente seleccionado desde el formulario
        
        # Obtener los datos del formulario de diagnóstico
        sintomas = request.form['sintomas']
        diagnostico = request.form['diagnostico']
        tratamiento = request.form['tratamiento']
        
        # Insertar la cita en la base de datos
        cursor = get_cursor()
        query = 'INSERT INTO citas (ID_Paciente, Fecha, Peso, Altura, Temperatura, LatidosPorMinuto, SaturacionOxigeno, Glucosa, Sintomas, Diagnostico, Tratamiento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (paciente_id, fecha, peso, altura, temperatura, latidos, saturacion, glucosa, sintomas, diagnostico, tratamiento))
        mysql.connection.commit()
        
        # Redireccionar a la página de consulta de citas después de guardar los datos
        flash('Cita exploración y diagnóstico guardada exitosamente!')
        return redirect(url_for('consultarCitas'))
    
    # Obtener la lista de pacientes registrados desde la base de datos
    cursor = get_cursor()
    query = 'SELECT ID, NombreCompleto FROM Pacientes'
    cursor.execute(query)
    pacientes = cursor.fetchall()

    # Mostrar la vista del formulario de cita exploración y diagnóstico
    return render_template('citaExploracion.html', pacientes=pacientes)




@app.route('/consultarCitas', methods=['GET', 'POST'])
def consultarCitas():
    if request.method == 'POST':
        RFC = request.form.get('RFC')
        
        # Obtener los valores de los filtros de nombre y fecha
        nombre = request.form.get('nombre')
        fecha = request.form.get('fecha')
        
        # Verificar si rfc es None y asignar cadena vacía en su lugar
        if RFC is None:
            RFC = ''

        # Realizar una consulta en la base de datos para obtener las citas del médico
        cursor = get_cursor()
        query = 'SELECT * FROM citas WHERE RFC LIKE %s AND Fecha = %s'
        cursor.execute(query, ('%' + RFC + '%', fecha))



        citas = cursor.fetchall()
        
        if citas:
            return render_template('consultarCitas.html', citas=citas)
        else:
            flash('No se encontraron citas para este médico.')
            return redirect(url_for('consultarCitas'))
    
    return render_template('consultarCitas.html')




@app.route('/mostrarRG')
def mostrarRG():
    return render_template('mostrarRG.html')

@app.route('/consultarPacientes')
def consultarPC():
    # Realizar una consulta en la base de datos para obtener los datos de los pacientes
    cursor = get_cursor()
    query = 'SELECT * FROM pacientes'
    cursor.execute(query)
    pacientes = cursor.fetchall()

    # Renderizar la plantilla y pasar los datos de pacientes como argumento
    return render_template('consultarPC.html', pacientes=pacientes)


# ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

