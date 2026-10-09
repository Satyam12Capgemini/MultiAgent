import asyncio
import os
import sys
from datetime import datetime, timezone
from sqlalchemy import select
from app.core.security import get_password_hash
from app.db.session import engine, Base, AsyncSessionLocal
from app.db.models import User, Customer, Order, OrderItem, Refund, KBDocument, KBChunk, EvalDataset, EvalCase
from app.rag.ingest import ingestion_service
from app.rag.chroma_store import chroma_store
from app.core.logging import setup_logging, logger

async def seed_data():
    print("[+] Initializing database tables & seeding demo customers, users, and orders...")
    setup_logging()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        existing_user = await session.execute(select(User).where(User.email == "aditya.sharma@example.com"))
        if existing_user.scalar_one_or_none():
            print("[OK] Demo accounts already present.")
            return

        # Create Customers
        c1 = Customer(id="cust-101", name="Aditya Sharma", email="aditya.sharma@example.com")
        c2 = Customer(id="cust-102", name="Priya Patel", email="priya.patel@example.com")
        c3 = Customer(id="cust-103", name="Rahul Verma", email="rahul.verma@example.com")
        session.add_all([c1, c2, c3])
        await session.flush()

        # Create Demo Users (Customer, Agent, Admin)
        # Password for all demo accounts: Password@123
        hashed_pwd = get_password_hash("Password@123")
        u1 = User(id="user-cust-1", email="aditya.sharma@example.com", password_hash=hashed_pwd, role="customer", customer_id=c1.id)
        u2 = User(id="user-agent-1", email="agent@supportcopilot.local", password_hash=hashed_pwd, role="agent", customer_id=None)
        u3 = User(id="user-admin-1", email="admin@supportcopilot.local", password_hash=hashed_pwd, role="admin", customer_id=None)
        session.add_all([u1, u2, u3])

        # Create Sample Orders
        o1 = Order(id="ORD-10023", customer_id=c1.id, total_amount=299.0, currency="INR", status="delivered", placed_at=datetime.now(timezone.utc))
        o2 = Order(id="ORD-10024", customer_id=c1.id, total_amount=1499.0, currency="INR", status="delivered", placed_at=datetime.now(timezone.utc))
        o3 = Order(id="ORD-20045", customer_id=c2.id, total_amount=499.0, currency="INR", status="placed", placed_at=datetime.now(timezone.utc))
        session.add_all([o1, o2, o3])
        await session.flush()

        # Order Items
        i1 = OrderItem(order_id=o1.id, product_name="Wi-Fi Range Extender N300", quantity=1, unit_price=299.0)
        i2 = OrderItem(order_id=o2.id, product_name="Gigabit Dual-Band Mesh Router Pro", quantity=1, unit_price=1499.0)
        i3 = OrderItem(order_id=o3.id, product_name="Cat6 Ethernet Cable (10m)", quantity=2, unit_price=249.5)
        session.add_all([i1, i2, i3])

        await session.commit()
        print("[OK] Seeding completed! Demo accounts:")
        print("   - Customer: aditya.sharma@example.com / Password@123")
        print("   - Agent:    agent@supportcopilot.local / Password@123")
        print("   - Admin:    admin@supportcopilot.local / Password@123")

async def ingest_samples(samples_dir: str = "../data/kb_samples"):
    print(f"[+] Ingesting sample KB documents from {samples_dir}...")
    setup_logging()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if not os.path.exists(samples_dir):
        # Check current dir relative path
        if os.path.exists("data/kb_samples"):
            samples_dir = "data/kb_samples"
        else:
            print(f"[ERROR] Directory {samples_dir} not found.")
            return

    async with AsyncSessionLocal() as session:
        for filename in os.listdir(samples_dir):
            filepath = os.path.join(samples_dir, filename)
            if not os.path.isfile(filepath):
                continue
            with open(filepath, "rb") as f:
                content = f.read()

            title = os.path.splitext(filename)[0].replace("_", " ").title()
            cat = "tech" if any(w in filename.lower() for w in ["router", "tech", "network", "wifi"]) else "general"

            print(f"   -> Ingesting '{title}' ({cat})...")
            await ingestion_service.ingest_document(
                session=session,
                title=title,
                category=cat,
                filename=filename,
                content=content,
                source=f"data/kb_samples/{filename}"
            )
    print("[OK] Ingestion complete. Vectors synced in ChromaDB and chunks in database.")

async def reset_db():
    print("[WARN] Resetting database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Database reset complete.")

async def reindex_kb():
    print("[+] Reindexing all chunks into ChromaDB...")
    async with AsyncSessionLocal() as session:
        await ingestion_service.refresh_bm25_index(session)
    print("[OK] Reindexing complete.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli [seed | ingest <dir> | reset-db | reindex]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "seed":
        asyncio.run(seed_data())
    elif cmd == "ingest":
        target = sys.argv[2] if len(sys.argv) > 2 else "data/kb_samples"
        asyncio.run(ingest_samples(target))
    elif cmd == "reset-db":
        asyncio.run(reset_db())
    elif cmd == "reindex":
        asyncio.run(reindex_kb())
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
