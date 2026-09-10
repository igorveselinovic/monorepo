from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

app = FastAPI()


data = {
    "plumbus": {"description": "Freshly pickled plumbus", "owner": "Morty"},
    "portal-gun": {"description": "Gun to create portals", "owner": "Rick"},
}


class InternalError(Exception):
    pass


class OwnerError(Exception):
    pass


def get_username():
    try:
        yield "Rick"
    except OwnerError as e:
        raise HTTPException(status_code=400, detail=f"Owner error: {e}")


def get_other_username():
    try:
        yield "Rick"
    except InternalError:
        print("We don't swallow the internal error here, we raise again 😎")
        raise


def get_another_username():
    try:
        yield "Rick"
    finally:
        print("Clean up before response is sent")


@app.get("/items/{item_id}")
def get_item(item_id: str, username: Annotated[str, Depends(get_username)]):
    if item_id not in data:
        raise HTTPException(status_code=404, detail="Item not found")
    item = data[item_id]
    if item["owner"] != username:
        raise OwnerError(username)
    return item


@app.get("/things/{thing_id}")
def get_thing(thing_id: str, username: Annotated[str, Depends(get_other_username)]):
    if thing_id == "portal-gun":
        raise InternalError(
            f"The portal gun is too dangerous to be owned by {username}"
        )
    if thing_id != "plumbus":
        raise HTTPException(
            status_code=404, detail="Thing not found, there's only a plumbus here"
        )
    return thing_id


@app.get("/users/me")
def get_user_me(username: Annotated[str, Depends(get_another_username, scope="function")]):
    return username
