import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from httpx import ASGITransport, AsyncClient
from decimal import Decimal


from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.models.user import User
from app.models.product import Product
from app.core.security import hash_password
from app.core.enums import OrderStatus
from app.models.order import Order, OrderItem


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(settings.TEST_DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db(test_engine):
    TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    async with TestSessionLocal() as session:
        await session.execute(text("""
        TRUNCATE TABLE
            order_items,
            orders,
            products,
            users
        RESTART IDENTITY CASCADE
        """))
        await session.commit()

        yield session


@pytest.fixture
async def client(db):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def user(db):
    user = User(
        username="Bob",
        hashed_password=hash_password('password'),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@pytest.fixture
async def product(db, user):

    product = Product(
        name="Product 1",
        price=Decimal(100.0),
        quantity=5,
        owner_id=user.id
    )

    db.add(product)
    await db.commit()

    await db.refresh(product)
    return product


@pytest.fixture
async def user_factory(db):
    async def _user_factory(**kwargs):
        defaults = {'username': 'Johnny_test', 'password': 'password'}

        defaults.update(kwargs)

        user = User(
            username=defaults['username'],
            hashed_password=hash_password(defaults['password'])
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    return _user_factory


@pytest.fixture
async def product_factory(db, user):
    async def _product_factory(**kwargs):
        defaults = {
            'name': 'test_product',
            'price': Decimal(100.0),
            'quantity': 5,
            'owner_id': user.id
        }

        defaults.update(kwargs)

        product = Product(**defaults)

        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    return _product_factory


@pytest.fixture
async def order(db, user, product):
    order = Order(
        user_id=user.id,
        total_price=Decimal(product.price *2),
        status=OrderStatus.PENDING,
        items=[
            OrderItem(
                product_id=product.id,
                quantity=2,
                price_at_order=product.price
            )
        ]
    )

    db.add(order)
    await db.commit()
    await db.refresh(order)

    return order