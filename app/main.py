import os

from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import router
from app.exception import validation_exception_handler, ServiceError, \
    service_error_handler, generic_exception_handler

app = FastAPI()

app.include_router(router.router)

app.add_exception_handler(ServiceError, service_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/static")


@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
