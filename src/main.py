from fastapi import FastAPI

from src.models.models import sample_products
from src.schemas import Feedback, UserCreate


app = FastAPI()

feedbacks = list()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/custom")
def read_custom_message():
    return {"message": "This is a custom message!"}


@app.post("/create_user")
def is_adult_user(user: UserCreate):
    return user


@app.post("/feedback")
def add_feedback(feedback: Feedback, is_premium: bool = False):
    feedbacks.append(dict(feedback))
    premium_text = " Ваш отзыв будет рассмотрен в приоритетном порядке." if is_premium else ""
    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён.{premium_text}", "total": len(feedbacks)}


@app.get("/product/search")
def get_feedback(keyword: str, category: str = None, limit: int = 10):
    products = [el for el in sample_products if keyword in el.get("name")]
    if category:
        products = [el for el in products if category == el.get("category")]
    return {"products": products[:limit]}


@app.get("/product/{product_id}")
def get_product(product_id: int):
    return [el for el in sample_products if el.get("product_id") == product_id][0]
