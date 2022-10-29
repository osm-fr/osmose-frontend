from fastapi import FastAPI

from modules.dependencies import database

from . import insight, update

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.startup()


# Add routes

app.include_router(insight.router)
app.include_router(update.router)
