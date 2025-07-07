from fastapi import FastAPI

from src.schemas import User


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/custom")
def read_custom_message():
    return {"message": "This is a custom message!"}


@app.post("/user")
def is_adult_user(user: User):
    is_adult = user.age > 17
    return {"name": user.name, "age": user.age, "is_adult": is_adult}
