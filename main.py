from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from routers import notifications, timetable
from pathlib import Path

app = FastAPI()

origins = [
    "https://sammyhost.uk",
    "https://www.sammyhost.uk",
    "*" # Allow all origins as no sensitive data is processed by the API (e.g. cookies/creds)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"], # You can be specific here for better security
    allow_headers=["*"],
)

app.include_router(notifications.router)
app.include_router(timetable.router)

@app.get("/ping")
def ping():
    return 'pong'
