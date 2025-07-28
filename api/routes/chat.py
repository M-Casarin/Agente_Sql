from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from utils.print_colors import Ppp
from services.sql_connector import ConsultadorSQL
from services.result_parser import ResultParser
from services.formatter import format_result
from services.llm_service import LLMService
from colorama import Fore as fre 

import html 
import time 


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

        # 2. Nuestro LLM debe traducir el mensaje a SQL 
        llm = LLMService()
        sql_query = await llm.ask_llm(message)
        print(fre.YELLOW + f"[LLM] SQL Query: {sql_query}" + fre.RESET) # debug 


        # try: 
        # 3. Ejecutar el SQL
        consultador = ConsultadorSQL(auth="local")
        result = consultador.execute_sql(sql_query)
        print(fre.YELLOW + f"[SQL] Result: {result}" + fre.RESET) # debug 
        print(fre.YELLOW + f"El tipo devuelto es {type(result)}" + fre.RESET) # debug

        # except Exception as e: 

        # Segun el tipo devuelto, ejucatmos una accion. 
        print(fre.YELLOW + f"[SQL] Result: {type(result)}" + fre.RESET) # debug
        # Respuesta sin formato, es solo texto
        if isinstance(result, str): 
           tipo_respuesta,  agent_html = "texto", f'<div class="msg bot">{html.escape(sql_query)}</div>'
           return user_html + agent_html
        
        # La respuesta es un diccionario, lo que implica que debe pintarse en pantalla como una tabla
        elif isinstance(result, dict): 
            tipo_respuesta, agent_html = format_result(result, formato="html")

        user_div = f"<div class='msg user'>{html.escape(message)}</div>"
        payload = html.escape(agent_html).replace("</", "<\\/")
        fid = f"form-panel-{int(time.time()*1000)}"

        return (
            user_div +
            "<div class='msg bot'>Resultado agregado al panel derecho. ➡️</div>"
            f"""
            <form id="{fid}" style="display:none">
            <input type="hidden" name="message" value="{html.escape(message)}">
            <input type="hidden" name="formatted_response" value="{payload}">
            </form>
            <script>
            const f = document.getElementById("{fid}");
            document.body.appendChild(f);
            fetch('/panel', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                body: new URLSearchParams(new FormData(f))
            }})
            .then(r => r.text())
            .then(html => {{
                document.getElementById('report-content')
                        .insertAdjacentHTML('beforeend', html);
                f.remove();
            }});
            </script>
            """
        )

    except Exception as e:
        Ppp.p(f"[Error.chat_agente] {e}", color="Green")
        return f'<div class="msg bot" style="color:red;">Error: {str(e)}</div>'


# Panel de graficos 
@router.post("/panel", response_class=HTMLResponse)
async def panel(message: str = Form(...), formatted_response: str = Form(...)):
    """
    Endpoint para agregar resultados al panel derecho. 

    - Recibe un mensaje del usuario y una respuesta formateada.
    - Devuelve un bloque HTML para insertar en el panel derecho.

    """
    try: 
        content = html.unescape(formatted_response)
        return f"<div><h4>{html.escape(message)}</h4>{content}<hr></div>"
    except Exception as e:
        Ppp.p(f"[Error.panel] {e}", color="Green")
        return f'<div class="msg bot" style="color:red;">Error: {str(e)}</div>'
