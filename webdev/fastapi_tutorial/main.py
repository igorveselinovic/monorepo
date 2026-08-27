import random
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from fastapi import Body, Cookie, FastAPI, Header, Path, Query
from pydantic import AfterValidator, BaseModel, Field, HttpUrl

app = FastAPI()

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class Image(BaseModel):
    url: HttpUrl
    name: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://www.example.com/",
                    "name": "Look at this graph",
                }
            ]
        }
    }

class Item(BaseModel):
    name: Annotated[str, Field(examples=["Foo"])]
    description: Annotated[str | None, Field(
        default=None, title="The description of the item", max_length=300, examples=["A very nice item"]
    )]
    price: Annotated[float, Field(gt=0, description="The price must be greater than zero", examples=[35.4])]
    tax: Annotated[float | None, Field(default=None, examples=[3.2])]
    tags: set[str] = set()
    images: list[Image] | None = None

class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]

class User(BaseModel):
    username: str
    full_name: str | None = None

class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: Annotated[int, Field(100, gt=0, le=100)]
    offset: Annotated[int, Field(0, ge=0)]
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []

def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: Annotated[str | None, Query(alias="item-query")]=None,
    size: Annotated[float | None, Query(gt=0, lt=10.5)]=None,
    ads_id: Annotated[str | None, Cookie()] = None,
    user_agent: Annotated[str | None, Header()] = None,
):
    results = {"item_id": item_id, "ads_id": ads_id, "user_agent": user_agent}
    if q:
        results.update({"q": q})
    if size:
        results.update({"size": size})
    return results

@app.get("/underscore_header_items/")
async def read_underscore_header_items(
    strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
):
    return {"strange_header": strange_header}

@app.get("/header_list_items/")
async def read_header_list_items(x_token: Annotated[list[str] | None, Header()] = None):
    return {"X-Token values": x_token}

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None,
        Query(
            alias="item-query",
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True,
        ),
    ] = None
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]

@app.get("/users")
async def read_users2():
    return ["Bean", "Elfo"]

@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

@app.get("/things/")
async def read_things(
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {"id": id, "name": item}

@app.get("/entities/")
async def read_entities(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer

@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images

@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights

@app.put("/items/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    item: Annotated[
        Item,
        Body(
            examples=[
                {
                    "name": "Bar",
                    "description": "A very very nice Item",
                    "price": 100.1,
                    "tax": 1.1,
                },
                {
                    "name": "Bar",
                    "price": "35.4",
                },
                {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            ]
        ),
    ],
    user: User,
    importance: Annotated[int, Body(gt=0)],
    q: str | None = None,
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results

@app.put("/things/{item_id}")
async def update_thing(
    item_id: int,
    item: Annotated[Item, Body(embed=True)]
):
    results = {"item_id": item_id, "item": item}
    return results

@app.put("/openapi_things/{item_id}")
async def update_openapi_things(
    *,
    item_id: int,
    item: Annotated[
        Item,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results

@app.put("/data_types_things/{item_id}")
async def read_data_types_thing(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }


# Cookie Parameter Models

class Cookies(BaseModel):
    model_config = {"extra": "forbid"}

    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None

@app.get("/cookies_items/")
async def read_cookies_items(cookies: Annotated[Cookies, Cookie()]):
    return cookies


# Header Parameter Models

class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []

@app.get("/headers_items/")
async def read_headers_items(headers: Annotated[CommonHeaders, Header()]):
    return headers

@app.get("/underscore_headers_items/")
async def read_underscore_headers_items(
    headers: Annotated[CommonHeaders, Header(convert_underscores=False)],
):
    return headers
