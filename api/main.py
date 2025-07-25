from  fastapi import FastAPI, Request 
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import HTMLResponse, FileResponse 
from fastapi.staticfiles import StaticFiles 
from fastapi.templating import Jinja2Templates 
from api.routes.chat import router as chat_router 
from utils.print_colors import Ppp


Ppp.p(f"Servicio Inicializado", color="Yellow")

# Instanciar la app 
app = FastAPI()

# agregar los routers 
app.include_router(router=chat_router)


# Midddleware
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Montar la carpeta de static 
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="views")


# Endpoints base 
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    print("Request for index page received")
    return templates.TemplateResponse('chat.html', {"request": request})



@app.get('/favicon.svg')
async def favicon(): 
    file_name = 'favicon.svg'
    file_path = './static/' + file_name
    return FileResponse(path=file_path, headers={'mimetype': 'image/svg+xml'})



