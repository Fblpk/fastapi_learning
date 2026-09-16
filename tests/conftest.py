import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from httpx import ASGITransport, AsyncClient
from decimal import Decimal

from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.models.user import User
from app.models.product import Product
from app.core.security import hash_password



@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(settings.TEST_DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db(test_engine):
    TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    async with TestSessionLocal() as session:
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
    async def _user(**kwargs):
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

    return _user


@pytest.fixture
async def products(db, user):
    owner = await user()

    p1 = Product(
        name="Product 1",
        price=Decimal(100.0),
        quantity=5,
        owner_id=owner.id
    )

    p2 = Product(
        name="Product 2",
        price=Decimal(200.0),
        quantity=10,
        owner_id=owner.id
    )

    p3 = Product(
        name="Product 3",
        price=Decimal(300.0),
        quantity=15,
        owner_id=owner.id
    )

    db.add_all([p1, p2, p3])
    await db.commit()

    await db.refresh(p1)
    await db.refresh(p2)
    await db.refresh(p3)

    return [p1, p2, p3]
