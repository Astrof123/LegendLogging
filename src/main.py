from fastapi import FastAPI
import hashlib
import datetime
import uvicorn
import logging
import sys

app = FastAPI()

from logging.handlers import TimedRotatingFileHandler

FORMATTER_STRING = "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "tmp/backend.log"

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)

    return logger

logger = get_logger("backend_logger")

@app.get("/auth")
async def root():
    with open("id/id_database.txt", "a+", encoding="utf-8") as f:
        while True:
            time_str = str(datetime.datetime.now())
            user_id = hashlib.md5(time_str.encode()).hexdigest()

            f.seek(0)
            sp = f.readlines()
            for line in sp:
                if line.strip() == user_id:
                    logger.warning(f"GET /auth — Повторился id: {user_id[0:6]}...")
                    continue

            f.write(f"{user_id}\n")
            break

    logger.info(f"GET /auth — Выдан id: {user_id[0:6]}...")
    return {"user_id": user_id}

if __name__ == "__main__":
    logger.info(f"Сервер запущен")
    uvicorn.run(app, host="0.0.0.0", port=8001)