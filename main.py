import os

from fastapi.requests import Request
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import router

app = FastAPI()

app.include_router(router.router)

app.mount("/static", StaticFiles(directory=os.path.join("app", "static")), name="static")
templates = Jinja2Templates(directory=os.path.join("app", "static"))


@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
