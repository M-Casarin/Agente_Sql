import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from openai import AsyncAzureOpenAI 
from typing import Optional
from core.config import (
    AZURE_OPENAI_API_KEY, 
    AZURE_OPENAI_API_VERSION, 
    AZURE_OPENAI_DEPLOYMENT_EMBEDDING_NAME, 
    AZURE_OPENAI_DEPLOYMENT_NAME, 
    AZURE_OPENAI_ENDPOINT, 
    AZURE_OPENAI_RESOURCE_NAME
)
import asyncio
from pathlib import Path


class LLMService(): 
    
    def __init__(self,
        system_prompt: Optional[str] = None    
    ):

        self.model_name = AZURE_OPENAI_DEPLOYMENT_NAME 
        self.system_prompt = system_prompt 
        try: 
            # Crear el cliente de Azure 
            self.client = AsyncAzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY, 
                api_version=AZURE_OPENAI_API_VERSION, 
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )

            self._load_system_prompt()
        except Exception as e:
            raise RuntimeError(f"Error al inicializar el cliente de Azure OpenAI: {str(e)}")
            # Un RuntimeError es una excepción que indica que ha ocurrido un error en tiempo de ejecución.
        except ValueError as ve:
            raise ValueError(f"Error de configuración: {str(ve)}")

    async def ask_llm(
        self, 
        user_message: str, 
        system_message: str = None,
        temperatura: float = 0.5, 
        chat_memory: list = None,
    ) -> str: 

        if temperatura > 1.0 or temperatura < 0: 
            raise ValueError("La temperaura debe tomar valores solo entre 0 y 1")
        if not isinstance(temperatura, (float, int)):
            raise TypeError("La temperatura debe ser un número.")

        # TODO: que el chatbot tenga memoria,
        messages = []

        # Si se incluye el system prompt
        if system_message or self.system_prompt: 
            messages.append(
                {"role": "system", "content": system_message or self.system_prompt}
            )

        # Si se incluye el chat memory
        if chat_memory: 
            for message in chat_memory: 
                messages.append(message)
                
        # Agregar el mensaje del usuario  
        messages.append(
            {"role": "user", "content": user_message}
        )
        try:
            # Generar peticion
            response = await self.client.chat.completions.create( 
                model=AZURE_OPENAI_DEPLOYMENT_NAME, 
                messages=messages, 
                temperature=temperatura, 
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Error al comunicarse con el modelo LLM: {str(e)}")
            # Un RuntimeError es una excepción que indica que ha ocurrido un error en tiempo de ejecución.

    def _load_system_prompt(self): 
        SYSTEM_PATH = Path("assets/system_prompt.txt")
        if SYSTEM_PATH.exists():
            with open(SYSTEM_PATH, "r", encoding="utf-8") as file:
                self.system_prompt = file.read()
        else:
            raise FileNotFoundError(f"El archivo {SYSTEM_PATH} no existe. Por favor, crea el archivo con el prompt del sistema.")


    def __repr__(self):
        return f"Servicio de Respuesta que implementa un modelo LLM para hacer consultas a AzureOpenai"



from utils.print_colors import Ppp
async def chat_loop(): 
    """
    Muestra el funcionamiento e interaccion con el sistema 
    """

    print("chatea con el agente, escribe 'q' para salir")
    llm = LLMService()
    while True: 
        try: 
            query = input("-> Habla con el LLM: ")
            Ppp.p(f"\n[Yo]: {query}", color="yellow")

            if query.lower() == 'q': 
                break
            answer = await llm.ask_llm(query)
            Ppp.p(f"[Agente 🤖]: {answer}", color="cyan")

        except Exception as e: 
            Ppp.p(f"\n[Error.chat_loop] {str(e)}", color="red")


if __name__ == '__main__': 
    asyncio.run(chat_loop())

