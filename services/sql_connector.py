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
    Clase para manejar la conexión y ejecución de consultas SQL
    en entornos local y productivo.
    """

    def __init__(self, auth: Literal['local', 'prod'] = 'local') -> None:
        """
        Inicializa la clase con la cadena de conexión adecuada.

        Args:
            auth (Literal['local', 'prod']): Tipo de conexión.
        """
        self.auth = auth
        self.connection_string = self._get_conn_str()
        if not self.test_connection():
            raise ValueError(f"[Error.ConsultadorSQL] No se pudo conectar al servidor con modo {auth}.")

    def _get_conn_str(self) -> str:
        """
        Devuelve la cadena de conexión ODBC según el entorno seleccionado.
        """
        base = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER_SQL};DATABASE={DATABASE};"
        if self.auth == "local":
            return base + "Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=yes;"
        elif self.auth == "prod":
            return base + f"UID={USER};PWD={PASSWORD};Encrypt=yes;TrustServerCertificate=yes;"
        else:
            raise ValueError(f"[Error.ConsultadorSQL] auth '{self.auth}' no es válido (usa 'local' o 'prod').")

    def test_connection(self) -> bool:
        """
        Verifica si la conexión con la base de datos funciona correctamente.
        """
        try:
            with pyodbc.connect(self.connection_string) as conn:
                return True
        except pyodbc.Error as e:
            Logger.error(f"[MODO]: {self.auth} | [Error.test_connection] {e}")
            return False

    def execute_sql(self, query: str) -> Dict[str, List]:
        """
        Ejecuta una consulta SQL y devuelve columnas y filas.

        Args:
            query (str): Consulta SQL.

        Returns:
            dict: {"columns": [...], "rows": [[...], [...]]}
        """
        try:
            with pyodbc.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    rows = [list(row) for row in cursor.fetchall()]

                    Logger.info(f"Consulta ejecutada con éxito: {query}")
                    return {"columns": columns, "rows": rows}
        except pyodbc.Error as e:
            Logger.error(f"[Error.execute_sql] {e}")
            raise RuntimeError(f"Error al ejecutar la consulta: {e}")

    def _get_chunks(self, query: str, chunk_size: int = 1000) -> Optional[Generator[pd.DataFrame, None, None]]:
        """
        Devuelve un generador de DataFrames en chunks para consultas grandes.
        """
        try:
            return pd.read_sql(query, pyodbc.connect(self.connection_string), chunksize=chunk_size)
        except pyodbc.Error as e:
            Logger.error(f"[Error._get_chunks] {e}")
            return None

    def create_df_from_table(self, query: str) -> pd.DataFrame:
        """
        Ejecuta una consulta SQL y devuelve el resultado como un DataFrame.

        Args:
            query (str): Consulta SQL.

        Returns:
            pd.DataFrame: DataFrame con los resultados.
        """
        if "SELECT" not in query.upper() or "FROM" not in query.upper():
            raise ValueError("La consulta debe contener SELECT y FROM.")

        try:
            chunks = self._get_chunks(query=query, chunk_size=1000)
            if chunks:
                return pd.concat(chunk for chunk in chunks)
            else:
                raise RuntimeError("No se devolvieron datos de la consulta.")
        except Exception as e:
            Logger.error(f"[Error.create_df_from_table] {e}")
            Ppp.p(str(e), color="Red")
            raise

    def create_df_from_query(self, query: str) -> Optional[pd.DataFrame]:
        """
        Crea un DataFrame usando SQLAlchemy + pyodbc.

        Args:
            query (str): Consulta SQL.

        Returns:
            pd.DataFrame | None
        """
        try:
            params = urllib.parse.quote_plus(self.connection_string)
            engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
            return pd.read_sql(query, engine)
        except Exception as e:
            Logger.error(f"[Error.create_df_from_query] {e}")
            return None


# Ejemplo de uso
if __name__ == "__main__":
    QUERY = "SELECT TOP 5 * FROM [Agente].[dbo].[HistorialChat]"
    consultador = ConsultadorSQL(auth='local')
    df = consultador.create_df_from_table(QUERY)
    result = consultador.execute_sql(QUERY)
    print(result["columns"])
    print(df.head())
