from datetime import datetime

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

fake_db = {}


class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


app = FastAPI()


@app.put("/items/{id}")
def update_item(id: str, item: Item):
    print("Raw pydantic object:", item)
    json_compatible_item_data = jsonable_encoder(item)
    print("JSON encoded dict:", json_compatible_item_data)
    fake_db[id] = json_compatible_item_data
    print("\"Database\" state:", fake_db)
