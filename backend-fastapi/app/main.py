
from fastapi import FastAPI

app = FastAPI(title="MessMetrics API")


@app.get("/")
def home():
    return {"message": "Welcome to MessMetrics API"}