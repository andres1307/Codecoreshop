import psycopg2

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="codecoreshop",
            user="postgres",
            password="Jo320872.",
            host="localhost",
            port="5432"
        )
        print("Conexión exitosa a la base de datos 'codecoreshop'")  # Depuración
        return conn
    except OperationalError as e:
        print("Error al conectar a la base de datos:")
        print(e)
        return None