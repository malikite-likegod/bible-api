from fastapi import FastAPI
from .routers import user, auth, translation, viewer, profile
from fastapi.middleware.cors import CORSMiddleware
from .database import SessionLocal
from .token_cleanup import start_cleanup_task

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(translation.router)
app.include_router(viewer.router)
app.include_router(profile.router)



@app.on_event("startup")
def start_event():
    start_cleanup_task(SessionLocal)

@app.get('/')
async def root():
    return {"message": "Hello, world!"}