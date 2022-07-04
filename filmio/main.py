from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .users import users_router
from .photos import photos_router
from .posts import posts_router

app = FastAPI()
app.include_router(users_router)
app.include_router(photos_router)
app.include_router(posts_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
