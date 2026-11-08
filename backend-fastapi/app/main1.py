from fastapi import FastAPI
from app.db import Base,engine
from app.models1 import TaskModel
from app.router1 import task_routes

Base.metadata.create_all(engine)


app=FastAPI(title="Fast API application")
app.include_router(task_routes)