import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pyodbc
import pandas as pd
import warnings
import urllib
from typing import Literal, Tuple, List, Dict, Optional, Generator
from sqlalchemy import create_engine
from core.config import SERVER_SQL, DATABASE, USER, PASSWORD
from services.logger import Logger
from utils.print_colors import Ppp

# Ignorar advertencias innecesarias de pandas
warnings.filterwarnings("ignore", category=UserWarning)

class ConsultadorSQL: 
    """
    Clase para manejar y ejecutar sentencias de SQL en nuestro servidor de SQL Server. 


    """

    def __init__(self, auth: Literal['local', 'prod']): 
        """ 
        Inicializa la con la cadena de conexión adecuada. 

        Args: 
            auth (Literal['local', 'prod']): tipo de conexión, local o productivo. 
        """
        self.auth = auth
        self.connection = self._get_connection()
        if not self.connection: 
            raise ValueError("[Error.ConsutadorSQL] Error al incializar ConsultadorSQL")


    def _get_conn_str(self) -> tuple[str |None,  str | None]:
        """
        Devuelve la cadena de conexion ODBC segun sea el entorno seleccionado.
        """
        if self.auth == "local":
            conn_str_local = (
                'DRIVER={ODBC Driver 18 for SQL Server};'
                f'SERVER={SERVER_SQL};'
                f'DATABASE={DATABASE};'
                'Trusted_Connection=yes;'
                'TrustServerCertificate=yes;'
                'Encrypt=yes;'
            )
            return conn_str_local, SERVER_SQL

        if self.auth == "prod":
            conn_str_prod = (
                'DRIVER={ODBC Driver 18 for SQL Server};'
                f"SERVER={SERVER_SQL};"
                f"DATABASE={DATABASE};"
                f"UID={USER};"
                f"PWD={PASSWORD};"
                "Encrypt=yes;"
                "TrustServerCertificate=yes;"
            )
            return conn_str_prod, SERVER_SQL 
        
        else: 
            raise ValueError(f"[Error.ConsultadorSQL._get_conn_str(self)] auth '{self.auth}' no es válido (usa 'local' o 'prod').")
        
        

    def _get_connection(self) : 
        """
        Establece una conexión a la base de datos y devuelve el objeto de conexión.
        Raises:
            ValueError: Si no se puede establecer la conexión.
        """

        try: 
            # Obtener la cadena de conexion, y el nombre del servidor
            conn_str, sv = self._get_conn_str()
            # Crear la conexion
            conn = pyodbc.connect(conn_str)
            # Mensaje sobre la conexion exitosa
            msg = f"[AUTH]: {self.auth} | Conexion Exitosa a la base de datos. "
            Logger.info(msg)
            return conn

        except pyodbc.Error as e:
            msg = f"[AUTH]: {self.auth} | [Error.get_connection] al conectar al servidor: {sv} :{e}"
            Logger.error(msg)
            return None 

    
    def execute_sql(self, query):
        """ 
        Ejecuta una consulta SQL y devuelve los resultados.

        Args: 
            query (str): sentencia SQL.
        Returns: 
            dict: {"columns": [...], "rows": [[...], [...]]}

        Raises:
            RuntimeError: Si ocurre un error al ejecutar la consulta.  
        """
        if not self.connection:
            raise ValueError("[Error.ConsultadorSQL.execute_sql] No hay conexión establecida.")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()

            # Validación: cada fila debe tener len() igual a columnas
            for row in rows:
                if len(row) != len(columns):
                    msg= f"[Error] Fila con {len(row)} valores pero se esperaban {len(columns)} columnas"
                    Logger.error(msg)
                    raise ValueError(msg)

            msg = f"Consulta realizada de forma exitosa: {query}"
            Logger.info(msg)
            # <-- AQUI el fix: asegúrate de convertir cada fila a lista
            return {"columns": columns, "rows": [list(row) for row in rows]}

        except Exception as e:
            msg = f"Error al ejecutar la consulta: {e}"
            Logger.info(msg)
            return "Error"
        
    def _get_chunks(
        self,
        query: str, 
        chunk_size: int = 1000
    ) -> pd.io.parsers.TextFileReader | None:
        """
        Devuelve los datos en chunks para evitar consumir demasiada memoria.
        """
        try:
            chunks = pd.read_sql(query, self.connection, chunksize=chunk_size)
            return chunks  
        except pyodbc.Error as e:
            print(f"Error al ejecutar el query: {e}")
            return None
    
    def create_df_from_table(
        self,
        query: str, 
    ) -> pd.DataFrame: 

        """
        La funcion creara una tabla a partir de una consulta que se ejecute segun el metodo. 
        Puede ser por cursor  por chunks.

        Args. 
            query (str): Cadena de consulta a ejecutar en sql. 
        Returns.
            pandas.DataFrame: es la tabla convertida en un dataframe. 
        """

        query_necesarias = ["SELECT", "FROM"]
        for necesaria in query_necesarias: 
            if not necesaria in query.upper(): 
                msg = "No ha ejecutado la consulta de forma adecuada"
                raise ValueError(msg)
                
        if self.connection: 
            try: 
                chunks = self._get_chunks(query=query, chunk_size=1000)
                if chunks: 
                    dframes = [chunk for chunk in chunks]
                    df_unido = pd.concat(dframes)
                    return df_unido
                
            except Exception as e: 
                msg = f"[Error.ConsultadorSQL.create_df_from_table] Error al crear la tabla: {e}"
                Ppp.p(msg, color="Red")
                Logger.error(msg)
        else: 
            return None

    # Obsoleta al menos localmente 
    def create_df_from_query(self, query: str):
        """
        Ejecuta una consulta SQL sobre la tabla DM_Produccion y muestra el resultado en un DataFrame.
        """
    
        try:
            params = urllib.parse.quote_plus(self._get_conn_str()).encode()
            Ppp.p(params, color="Yellow")
            params = urllib.parse.quote_from_bytes(params.encode())
            engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
            df = pd.read_sql(query, engine)
            print(df)
            return df
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return None
        

# Ejemplo de uso
if __name__ == "__main__":

    consultador = ConsultadorSQL(auth='local')
    QUERY_CHAT = """
        SELECT TOP 5 * FROM [Agente].[dbo].[Historial_Chat]
    """

    QUERY_EFECTIVIDAD = """ 
        SELECT * FROM [RPA].[dbo].[Efectividad_Andromeda]; 
    """

    # Ejecuta la sentencia y devuelve las columas y filas
    result = consultador.execute_sql(QUERY_CHAT)
    print(result)

    # A partir de la consulta crea un DataFrame
    df = consultador.create_df_from_table(QUERY_CHAT)
    print(df)

    # Efectividad 
    result_efectividad = consultador.execute_sql(QUERY_EFECTIVIDAD)
    print(result_efectividad)