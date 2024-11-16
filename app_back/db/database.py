"""Este módulo se encarga de la conexión a la base de datos."""

import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Conecta a la base de datos y retorna la conexión."""

    
    connection = None
    try:
        connection = mysql.connector.connect(
            host='autorack.proxy.rlwy.net',
            user='root',
            password='dQEtcVjUNYnrguKbGireIdKRysgtNvxT',  
            database='treevitality',
            port=19371
        )
        if connection.is_connected():
            print("Conexión a la base de datos exitosa")
    except Error as e:
        print(f"Error: '{e}'")

    return connection

if __name__ == "__main__":
    conn = get_db_connection()
