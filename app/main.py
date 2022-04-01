from typing import Optional
from fastapi import FastAPI
from app.haproxy.routers import haproxy

app = FastAPI()

app.include_router(haproxy.router)



