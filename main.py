from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "FastAPI UI Example"})


@app.get("/api/hello")
async def api_hello():
    return JSONResponse({"message": "Hello from API"})


from routes import router as devices_router

app.include_router(devices_router, prefix="/api", tags=["devices"])