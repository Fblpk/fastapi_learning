from fastapi import FastAPI
from app.core.database import engine
from app.models.product import Base
from app.api.products import router as products_router

# Создание таблиц (в будущем это заменит Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="My E-Commerce API")

# Подключаем роутер товаров к главному приложению
app.include_router(products_router)

@app.get('/')
def home():
    return {'message': 'Магазин работает'}







