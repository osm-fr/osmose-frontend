from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.dependencies import database

from . import false_positive, issue, issues, issues_tiles, meta_0_3, user

app = FastAPI()


# class OsmoseAPIBottle(bottle.Bottle):
#     def default_error_handler(self, res):
#         bottle.response.content_type = 'text/plain'
#         return res.body

# CORS middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)


@app.on_event("startup")
async def startup():
    await database.startup()


# Add routes

app.include_router(meta_0_3.router)
app.include_router(user.router)
app.include_router(issue.router)
app.include_router(issues.router)
app.include_router(issues_tiles.router)
app.include_router(false_positive.router)
