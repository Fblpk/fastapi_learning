from fastapi import FastAPI
from app.api.products import router as products_router
from app.api.auth import router as auth_router
from app.api.orders import router as orders_router

app = FastAPI(title="My E-Commerce API")


app.include_router(products_router)
app.include_router(auth_router)
app.include_router(orders_router)

@app.get('/')
def home():
    return {'message': 'Магазин работает'}