from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.app_config import AppConfig
from config.db_config import DBConfig

app = FastAPI()

app_config = AppConfig()
db_config = DBConfig()

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
