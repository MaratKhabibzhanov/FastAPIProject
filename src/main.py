from fastapi import FastAPI

from src.schemas import User

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/custom")
def read_custom_message():
    return {"message": "This is a custom message!"}


@app.get("/users")
def read_first_user():
    first_user = User(id=1, name="John Doe")
    return first_user