from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse



router = APIRouter(prefix="/products", tags=["Products"])


def find_product(id: int, db: Session):
    product = db.query(Product).filter(Product.id == id).first()

    if product:
        return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )

@router.post('/', response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(
        name=product.name,
        price=product.price,
        quantity=product.quantity
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.put('/{id}', response_model=ProductResponse)
def update_product(id: int, product: ProductCreate, db: Session = Depends(get_db)):
    product_to_update = find_product(id, db)

    product_to_update.name = product.name
    product_to_update.price = product.price
    product_to_update.quantity = product.quantity

    db.commit()
    db.refresh(product_to_update)

    return product_to_update


@router.delete('/{id}')
def delete_product(id: int, db: Session = Depends(get_db)):
    product_to_delete = find_product(id, db)

    db.delete(product_to_delete)
    db.commit()

    return {'deleted': product_to_delete}



@router.get('/{id}', response_model=ProductResponse)
def get_product(id: int, db: Session = Depends(get_db)):
    return find_product(id, db)



@router.get('/', response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    return db.query(Product).all()