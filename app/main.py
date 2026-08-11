from fastapi import FastAPI
from app.api.products import router as products_router

app = FastAPI(title="My E-Commerce API")

# Подключаем роутер товаров к главному приложению
app.include_router(products_router)

@app.get('/')
def home():
    return {'message': 'Магазин работает'}