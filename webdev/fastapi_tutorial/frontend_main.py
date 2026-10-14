from fastapi import FastAPI

app = FastAPI()

app.frontend("/", directory="frontend_dist")
