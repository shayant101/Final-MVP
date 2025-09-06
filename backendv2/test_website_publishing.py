import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status

from app.main import app
from app.database import get_database
from app.auth import create_access_token
from app.models_website_builder import WebsiteStatus

# Test data
TEST_RESTAURANT_ID = "60c72b9f9b1d8c001f8e4c8b"
TEST_WEBSITE_ID = "test_website_123"
TEST_USER_ID = "test_user_123"

@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(base_url="http://localhost:3000") as client:
        yield client

from app.database import connect_to_mongo, close_mongo_connection

@pytest_asyncio.fixture(scope="function")
async def db():
    # This fixture now just provides the db object,
    # the connection is handled by the override
    yield get_database()

@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_get_db():
    await connect_to_mongo()
    app.dependency_overrides[get_database] = get_database
    yield
    # Clean up all test data
    database = get_database()
    await database.users.delete_many({"restaurant_id": TEST_RESTAURANT_ID})
    await database.websites.delete_many({"restaurant_id": TEST_RESTAURANT_ID})
    await close_mongo_connection()
    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
def auth_headers():
    token = create_access_token(data={"user_id": TEST_USER_ID, "restaurant_id": TEST_RESTAURANT_ID, "role": "restaurant"})
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_publish_website(async_client, db, auth_headers):
    # Create a test user and website
    await db.users.insert_one({"user_id": TEST_USER_ID, "restaurant_id": TEST_RESTAURANT_ID})
    await db.websites.insert_one({
        "website_id": TEST_WEBSITE_ID,
        "restaurant_id": TEST_RESTAURANT_ID,
        "website_name": "Test Restaurant",
        "status": WebsiteStatus.draft.value,
        "pages": [{"is_homepage": True}],
        "seo_settings": {"site_title": "Test", "site_description": "Test"}
    })

    # Test publishing
    response = await async_client.post(f"/api/website-builder/websites/{TEST_WEBSITE_ID}/publish", headers=auth_headers, json={})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["live_url"] is not None

    # Verify website status
    website = await db.websites.find_one({"website_id": TEST_WEBSITE_ID})
    assert website["status"] == WebsiteStatus.published.value
    assert website["has_unpublished_changes"] is False

@pytest.mark.asyncio
async def test_unpublish_website(async_client, db, auth_headers):
    # Create a test user and website
    await db.users.insert_one({"user_id": TEST_USER_ID, "restaurant_id": TEST_RESTAURANT_ID})
    await db.websites.insert_one({
        "website_id": TEST_WEBSITE_ID,
        "restaurant_id": TEST_RESTAURANT_ID,
        "status": WebsiteStatus.published.value,
    })

    # Test unpublishing
    response = await async_client.post(f"/api/website-builder/websites/{TEST_WEBSITE_ID}/unpublish", headers=auth_headers, json={})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True

    # Verify website status
    website = await db.websites.find_one({"website_id": TEST_WEBSITE_ID})
    assert website["status"] == WebsiteStatus.draft.value

@pytest.mark.asyncio
async def test_get_publish_status(async_client, db, auth_headers):
    # Create a test user and website
    await db.users.insert_one({"user_id": TEST_USER_ID, "restaurant_id": TEST_RESTAURANT_ID})
    await db.websites.insert_one({
        "website_id": TEST_WEBSITE_ID,
        "restaurant_id": TEST_RESTAURANT_ID,
        "status": WebsiteStatus.draft.value,
    })

    # Test getting publish status
    response = await async_client.get(f"/api/website-builder/websites/{TEST_WEBSITE_ID}/publish-status", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["website_id"] == TEST_WEBSITE_ID
    assert data["status"] == WebsiteStatus.draft.value