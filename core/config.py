"""
El modulo carga las variables de entorno
"""

from dotenv import load_dotenv
import os 


load_dotenv()

# Para llm_service
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION= os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_RESOURCE_NAME = os.getenv("AZURE_OPENAI_RESOURCE_NAME")
AZURE_OPENAI_DEPLOYMENT_EMBEDDING_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING_NAME")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Para sql_connector
SERVER_SQL = os.getenv("SERVER_SQL")
DATABASE = os.getenv("DATABASE")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD", "")