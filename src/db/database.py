from passlib.handlers.bcrypt import bcrypt

from src.models.models import RoleEnum, UserInDB


sample_product_1 = {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99}

sample_product_2 = {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99}

sample_product_3 = {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99}

sample_product_4 = {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99}

sample_product_5 = {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99}

sample_products = [sample_product_1, sample_product_2, sample_product_3, sample_product_4, sample_product_5]


fake_users_db = [
    UserInDB(username="admin", hashed_password=bcrypt.hash("pass1"), role=RoleEnum.ADMIN),
    UserInDB(username="alice", hashed_password=bcrypt.hash("pass1"), role=RoleEnum.USER),
    UserInDB(username="bob", hashed_password=bcrypt.hash("pass1"), role=RoleEnum.USER),
    UserInDB(username="guest", hashed_password=bcrypt.hash("pass1"), role=RoleEnum.GUEST),
]
cookie_cache = dict()

refresh_tokens = dict()

resources = {
    "alice": {"content": "Секретные данные Алисы", "is_public": False},
    "bob": {"content": "Публичные заметки Боба", "is_public": True},
    "admin": {"content": "Админский ресурс", "is_public": False},
}
