from fastapi import FastAPI, APIRouter
from utils.print_colors import Ppp 

# instanciar el router 
router = APIRouter()

@router.post("/chat")
async def chat_agente(): 
    ... 