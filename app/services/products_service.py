from sqlalchemy.orm import Session
from fastapi import HTTPException



from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate


def find_product(
        id: int,
        db: Session
):
    product = db.query(Product).filter(Product.id == id).first()

    if product:
        return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


def create_product(
        product: ProductCreate,
        db: Session,
        current_user: User
):

    new_product = Product(
        name=product.name,
        price=product.price,
        quantity=product.quantity,
        owner_id=current_user.id
    )


    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


def update_product(
        id: int, product: ProductCreate,
        db: Session,
        current_user: User
):

    product_to_update = find_product(id, db)

    if product_to_update.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail='Forbidden'
        )

    product_to_update.name = product.name
    product_to_update.price = product.price
    product_to_update.quantity = product.quantity

    db.commit()
    db.refresh(product_to_update)

    return product_to_update


def delete_product(
        id: int,
        db: Session,
        current_user: User
):
    product_to_delete = find_product(id, db)

    if product_to_delete.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail='Forbidden'
        )

    db.delete(product_to_delete)
    db.commit()

    return {'deleted': True, 'id': id}


def get_product(
        id: int,
        db: Session
):
    return find_product(id, db)


def get_all_products(
        db: Session,
        limit: int,
        offset: int,
        search: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
):
    query = db.query(Product)

    if search:
        query = query.filter(Product.name.contains(search))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    return query.limit(limit).offset(offset).all()