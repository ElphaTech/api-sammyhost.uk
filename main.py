from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://sammyhost.uk",
    "https://www.sammyhost.uk",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"], # You can be specific here for better security
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return 'pong'
