from fastapi import FastAPI
from pydantic import BaseModel
from service import CAG
from time import time


app = FastAPI()
# Создание экземпляра сервиса CAG
service = CAG()

class UserRequest(BaseModel):
    # Модель запроса пользователя
    query: str

@app.pos("/query")
def process_query(query: UserRequest):
    # Обработка запроса пользователя
    start_time = time()
    response = service.process_query(query)

    return {
        "content": response,
        "time_elapsed": time() - start_time
    }