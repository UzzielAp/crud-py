"""Este módulo se encarga de gestionar los reportes ambientales. """

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import bcrypt 
from .db.database import get_db_connection
from mysql.connector import Error

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://tree-vitality-production.up.railway.app"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   
    allow_credentials=True,
    allow_methods=["*"],     
    allow_headers=["*"], 
)

@app.get("/")
async def read_root():
    return {"mensaje": "Bienvenido a la API de reportes ambientales"}

class Reporte(BaseModel):
    """Modelo que representa un reporte ambiental."""
    usuario_id: int
    nombre: str
    email_rep: str
    ubicacion: str
    tipo_reporte: str
    descripcion: str


@app.post("/reportes/")
async def crear_reporte(reporte: Reporte):
    """Crea un nuevo reporte ambiental en la base de datos."""
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")

    try:
        cursor = connection.cursor()

        sql = """INSERT INTO reportes_ambientales (usuario_id, nombre, email_rep, ubicacion, tipo_reporte, descripcion) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (reporte.usuario_id, reporte.nombre, reporte.email_rep, reporte.ubicacion, reporte.tipo_reporte, reporte.descripcion)

        cursor.execute(sql, values)
        connection.commit()
        return {"mensaje": "Reporte creado exitosamente"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar en la base de datos: {e}") from e  
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/reporte/")
async def obtener_reportes():
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")

    try:
        cursor = connection.cursor(dictionary=True)
        # Consulta con JOIN para obtener los reportes y el nombre del usuario
        cursor.execute("""
            SELECT 
                r.id, 
                r.nombre, 
                r.email_rep, 
                r.ubicacion, 
                r.tipo_reporte, 
                r.descripcion, 
                r.fecha_reporte, 
                u.nombre AS usuario
            FROM reportes_ambientales r
            JOIN usuarios u ON r.usuario_id = u.id
        """)
        reportes = cursor.fetchall()

        if not reportes:
            return {"mensaje": "No hay reportes disponibles"}
        
        return {"reportes": reportes}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reportes: {e}") from e
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

class Contactenos(BaseModel):
    """Modelo que representa un reporte ambiental."""
    nombre: str
    email_rep: str
    tema: str
    mensaje: str


@app.post("/contactenos/")
async def crear_contacto(contactenos: Contactenos):
    """Crea un nuevo reporte ambiental en la base de datos."""
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")

    try:
        cursor = connection.cursor()

        sql = """INSERT INTO contactenos (nombre, email_rep, tema, mensaje) 
                 VALUES (%s, %s, %s, %s)"""
        values = ( contactenos.nombre, contactenos.email_rep, contactenos.tema, contactenos.mensaje)

        cursor.execute(sql, values)
        connection.commit()
        return {"mensaje": "Mnesaje Enviado exitosamente"}
    
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar en la base de datos: {e}") from e  
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

class Usuarios(BaseModel):
    """Modelo que representa un reporte ambiental."""
    nombre: str
    email: str
    password: str

@app.post("/signup/")
async def crear_usuario(usuario: Usuarios):
    """Crea un nuevo usuario en la base de datos."""
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")

    try:
        cursor = connection.cursor()

        # Verificar si el email ya está registrado
        sql_check = "SELECT * FROM usuarios WHERE email = %s"
        cursor.execute(sql_check, (usuario.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")

        # Hash de la contraseña usando bcrypt
        hashed_password = bcrypt.hashpw(usuario.password.encode('utf-8'), bcrypt.gensalt())

        # Crear el nuevo usuario
        sql_insert = """INSERT INTO usuarios (nombre, email, password, tipo_usuario) 
                        VALUES (%s, %s, %s, 'usuario')"""
        values = (usuario.nombre, usuario.email, hashed_password)

        cursor.execute(sql_insert, values)
        connection.commit()

        return {"mensaje": "Usuario creado exitosamente"}

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar en la base de datos: {e}") from e

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


class Login(BaseModel):
    """Modelo que representa un login."""
    email: str
    password: str


@app.post("/login/")
async def login(credentials: Login):
    """Inicia sesión de un usuario."""
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")

    try:
        cursor = connection.cursor()
        sql = "SELECT id, password FROM usuarios WHERE email = %s"  
        cursor.execute(sql, (credentials.email,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code=400, detail="Credenciales incorrectas")

        usuario_id, hashed_password = result  

        # Verificar la contraseña usando bcrypt
        if not bcrypt.checkpw(credentials.password.encode('utf-8'), hashed_password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Credenciales incorrectas")
        return {
            "mensaje": "Inicio de sesión exitoso",
            "usuario_id": usuario_id 
        }

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar las credenciales: {e}") from e
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

class Actividad(BaseModel):
    """Modelo que representa la inscripción actividad."""
    usuario_id: int
    tipo_actividad: str
    nombre: str
    email: str
    telefono: str

@app.post("/inscripcion_actividad/")
async def incripcion_actividad(actividad: Actividad):
    """Crea un nueva inscripción para actividad en la base de datos."""
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")

    try:
        cursor = connection.cursor()

        sql = """INSERT INTO inscripciones_actividades (usuario_id, tipo_actividad, nombre, email, telefono) 
                 VALUES (%s, %s, %s, %s, %s)"""
        values = (actividad.usuario_id, actividad.tipo_actividad, actividad.nombre, actividad.email, actividad.telefono )

        cursor.execute(sql, values)
        connection.commit()
        return {"mensaje": "inscripción creada exitosamente"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar en la base de datos: {e}") from e  
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()