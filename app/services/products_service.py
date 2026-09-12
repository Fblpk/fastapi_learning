from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate


async def find_product(id: int, db: AsyncSession):
    stmt = select(Product).filter(Product.id == id)
    product = (await db.execute(stmt)).scalars().first()

    if product:
        return product

    raise HTTPException(status_code=404, detail="Product not found")


async def create_product(product: ProductCreate, db: AsyncSession, current_user: User):

    new_product = Product(
        name=product.name,
        price=product.price,
        quantity=product.quantity,
        owner_id=current_user.id,
    )

    db.add(new_product)
    await db.commit()

    return new_product


async def update_product(id: int, product: ProductCreate, db: AsyncSession, current_user: User):
    product_to_update = await find_product(id, db)

    if product_to_update.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    product_to_update.name = product.name
    product_to_update.price = product.price
    product_to_update.quantity = product.quantity

    await db.commit()

    return product_to_update


async def delete_product(id: int, db: AsyncSession, current_user: User):
    product_to_delete = await find_product(id, db)

    if product_to_delete.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await db.delete(product_to_delete)
    await db.commit()

    return {"deleted": True, "id": id}


async def get_product(id: int, db: AsyncSession):
    return await find_product(id, db)


async def get_all_products(
    db: AsyncSession,
    limit: int,
    offset: int,
    search: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
):
    stmt = select(Product)

    if search:
        stmt = stmt.filter(Product.name.contains(search))
    if min_price is not None:
        stmt = stmt.filter(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.filter(Product.price <= max_price)

    result = await db.execute(stmt.limit(limit).offset(offset))
    return result.scalars().all()