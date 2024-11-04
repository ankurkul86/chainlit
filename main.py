from typing import Optional

from fastapi import FastAPI

from chainlit.utils import mount_chainlit

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Optional[str] = None):
#     return {"item_id": item_id, "q": q}

# Mount the Chainlit application
mount_chainlit(app=app, target="my_cl_app.py", path="/chainlit")
