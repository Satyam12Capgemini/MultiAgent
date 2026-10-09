import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import engine, Base
from app.cli import seed_data

@pytest_asyncio.fixture(autouse=True)
async def init_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_data()
    yield

@pytest.mark.asyncio
async def test_health_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

        resp_ready = await client.get("/api/v1/health/ready")
        assert resp_ready.status_code == 200
        assert resp_ready.json()["status"] == "ready"

@pytest.mark.asyncio
async def test_auth_login_and_ticket_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "aditya.sharma@example.com",
            "password": "Password@123"
        })
        assert login_resp.status_code == 200
        data = login_resp.json()
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get Me
        me_resp = await client.get("/api/v1/auth/me", headers=headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "aditya.sharma@example.com"

        # 3. Create Ticket
        ticket_resp = await client.post("/api/v1/tickets", headers=headers, json={
            "message": "How do I factory reset my router?",
            "subject": "Router Reset Question"
        })
        assert ticket_resp.status_code == 201
        t_data = ticket_resp.json()
        assert "ticket_id" in t_data
        assert "run_id" in t_data
