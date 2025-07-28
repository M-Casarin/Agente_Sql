from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from utils.print_colors import Ppp
from services.sql_connector import ConsultadorSQL
from services.result_parser import ResultParser
from services.llm_service import LLMService

router = APIRouter()

@router.post("/chat", response_class=HTMLResponse)
async def chat_agente(message: str = Form(...)):
    """
    Endpoint principal del chat.
    - Recibe un mensaje del usuario.
    - Llama al LLM para generar SQL.
    - Ejecuta el SQL en la base de datos.
    - Devuelve un bloque HTML para insertar en el chat-log.
    """

    try:
        # 1. Mostrar mensaje del usuario
        user_html = f'<div class="msg user">{message}</div>'

        # 2. LLM traduce a SQL
        llm = LLMService()
        prompt = f"Convierte la siguiente consulta en SQL válido: {message}"
        sql_query = await llm.ask_llm(prompt)

        # 3. Ejecutar el SQL
        consultador = ConsultadorSQL(auth="local")
        result = consultador.execute_sql(sql_query)

        # 4. Parsear resultados
        parser = ResultParser()
        parsed = parser.parse_result(result["columns"], result["rows"])
        table_html = parsed["html"]

        # 5. Bloque de respuesta
        agent_html = (
            f'<div class="msg bot">'
            f"<p><b>SQL:</b> {sql_query}</p>{table_html}"
            f'</div>'
        )

        return user_html + agent_html

    except Exception as e:
        Ppp.p(f"[Error.chat_agente] {e}", color="red")
        return f'<div class="msg bot" style="color:red;">Error: {str(e)}</div>'
