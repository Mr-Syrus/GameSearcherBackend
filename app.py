import logging

import uvicorn

import config
import incelization
from fastapi.middleware.cors import CORSMiddleware

# Initialization
incelization.init()

app = config.APP

origins = [
    "http://localhost:5173",  # фронтенд
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # разрешаем конкретные домены
    allow_credentials=True,
    allow_methods=["*"],          # разрешаем все методы
    allow_headers=["*"],          # разрешаем все заголовки
)

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090, log_level="info")
