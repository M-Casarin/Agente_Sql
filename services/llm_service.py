import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from openai import AsyncAzureOpenAI 
from typing import Optional
import os 
from typing import Optional
from core.config import (
    AZURE_OPENAI_API_KEY, 
    AZURE_OPENAI_API_VERSION, 
    AZURE_OPENAI_DEPLOYMENT_EMBEDDING_NAME, 
    AZURE_OPENAI_DEPLOYMENT_NAME, 
    AZURE_OPENAI_ENDPOINT, 
    AZURE_OPENAI_RESOURCE_NAME
)
from services.logger import Logger 
import asyncio

class LLMService(): 
    
    def __init__(self,
        model_name: Optional[str] = None, 
        system_prompt: Optional[str] = None    
    ):

        self.model_name = model_name or AZURE_OPENAI_DEPLOYMENT_NAME 

        # Crear el cliente de Azure 
        self.client = AsyncAzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY, 
            api_version=AZURE_OPENAI_API_VERSION, 
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
    
    async def ask_llm(
        self, 
        user_message: str, 
        system_message: str = None,
        temperatura: float = 0.5, 
        chat_memory_id: int = 0, # Verificar si aqui es donde mas conviene insertar el id de la memoria
    ) -> str: 

        if temperatura > 1.0 or temperatura < 0: 
            raise ValueError("La temperaura debe tomar valores solo entre 0 y 1")
        if isinstance(temperatura, int): 
            temperatura = float(temperatura)

        # TODO: que el chatbot tenga memoria,
        messages = []

        # Si se incluye el system prompt
        if system_message: 
            messages.append(
                {"role": "system", "content": system_message}
            )
        messages.append(
            {"role": "user", "content": user_message}
        )

        # Generar peticion
        response = await self.client.chat.completions.create( 
            model=AZURE_OPENAI_DEPLOYMENT_NAME, 
            messages=messages, 
            temperature=temperatura, 
            max_tokens=500
        )

        return response.choices[0].message.content

    def __repr__(self):
        print(f"Servicio de Respuesta que implementa un modelo LLM para hacer consultas a AzureOpenai")


from utils.print_colors import Ppp
async def chat_loop(): 
    """
    Muestra el funcionamiento e interaccion con el sistema 
    """

    print("chatea con el agente, escribe 'q' para salir")
    llm = LLMService()
    while True: 
        try: 
            query = input("-> Habla con el LLM")
            Ppp.p(f"\n[Yo]: {query}", color="yellow")

            if query.lower() == 'q': 
                break
            answer = await llm.ask_llm(query)
            Ppp.p(f"[Agente 🤖]: {answer}", color="cyan")

        except Exception as e: 
            Ppp.p(f"\n[Error.chat_loop] {str(e)}")


if __name__ == '__main__': 
    asyncio.run(chat_loop())

