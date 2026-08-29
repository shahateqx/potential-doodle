"""Seed script — creates demo data for evaluation.

Run: python seed.py

Creates:
- 2 users (tenants)
- 2 widgets per user
- 5 sample submissions
"""

import asyncio
import uuid
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.database import async_session, engine, Base
from app.models.user import User
from app.models.widget import Widget, WidgetType
from app.models.submission import Submission
from app.routers.auth import hash_password
from datetime import datetime, timezone, timedelta


async def seed():
    """Create demo data."""
    async with engine.begin() as conn:
        # Create tables if they don't exist (fallback if migrations haven't run)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Check if data already exists
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        if count > 0:
            print("⚠️  Database already has data. Skipping seed.")
            return

        # ─── User 1 (Tenant A) ───
        user_a = User(
            id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            email="alice@example.com",
            hashed_password=hash_password("password123"),
            name="Alice (Tenant A)",
        )
        session.add(user_a)

        # ─── User 2 (Tenant B) ───
        user_b = User(
            id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            email="bob@example.com",
            hashed_password=hash_password("password123"),
            name="Bob (Tenant B)",
        )
        session.add(user_b)
        await session.flush()

        # ─── Widgets for User A ───
        widget_a1 = Widget(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            owner_id=user_a.id,
            widget_type=WidgetType.SIGNUP_FORM,
            title="Newsletter Signup",
            description="Subscribe to our weekly newsletter!",
            form_fields=[
                {"name": "email", "label": "Email", "field_type": "email", "required": True, "placeholder": "your@email.com"},
                {"name": "name", "label": "Name", "field_type": "text", "required": False, "placeholder": "Your name"},
            ],
            button_text="Subscribe",
            display_options={"color": "#4F46E5", "background_color": "#FFFFFF", "text_color": "#1F2937", "position": "bottom-right", "border_radius": "8px"},
        )
        session.add(widget_a1)

        widget_a2 = Widget(
            id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
            owner_id=user_a.id,
            widget_type=WidgetType.CONTACT_FORM,
            title="Contact Us",
            description="We'd love to hear from you!",
            form_fields=[
                {"name": "email", "label": "Email", "field_type": "email", "required": True, "placeholder": "your@email.com"},
                {"name": "name", "label": "Name", "field_type": "text", "required": True, "placeholder": "Your name"},
                {"name": "message", "label": "Message", "field_type": "textarea", "required": True, "placeholder": "Your message..."},
            ],
            button_text="Send Message",
            display_options={"color": "#059669", "background_color": "#F0FDF4", "text_color": "#1F2937", "position": "center", "border_radius": "12px"},
        )
        session.add(widget_a2)

        # ─── Widget for User B ───
        widget_b1 = Widget(
            id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
            owner_id=user_b.id,
            widget_type=WidgetType.CTA_POPOVER,
            title="Get 20% Off!",
            description="Sign up now for an exclusive discount.",
            form_fields=[
                {"name": "email", "label": "Email", "field_type": "email", "required": True, "placeholder": "your@email.com"},
            ],
            button_text="Claim Discount",
            display_options={"color": "#DC2626", "background_color": "#FEF2F2", "text_color": "#1F2937", "position": "bottom-right", "border_radius": "16px"},
        )
        session.add(widget_b1)
        await session.flush()

        # ─── Sample Submissions ───
        now = datetime.now(timezone.utc)
        submissions = [
            Submission(
                widget_id=widget_a1.id,
                data={"email": "visitor1@test.com", "name": "Visitor One"},
                ip_address="8.8.8.8",
                geo_country="United States",
                geo_city="Mountain View",
                geo_region="California",
                created_at=now - timedelta(days=2),
            ),
            Submission(
                widget_id=widget_a1.id,
                data={"email": "visitor2@test.com", "name": "Visitor Two"},
                ip_address="1.1.1.1",
                geo_country="Australia",
                geo_city="Sydney",
                geo_region="New South Wales",
                created_at=now - timedelta(days=1),
            ),
            Submission(
                widget_id=widget_a2.id,
                data={"email": "contact@test.com", "name": "Contactor", "message": "Hello!"},
                ip_address="9.9.9.9",
                geo_country="Germany",
                geo_city="Berlin",
                geo_region="Berlin",
                created_at=now - timedelta(hours=6),
            ),
            Submission(
                widget_id=widget_b1.id,
                data={"email": "shopper@test.com"},
                ip_address="208.67.222.222",
                geo_country="United States",
                geo_city="San Francisco",
                geo_region="California",
                created_at=now - timedelta(hours=3),
            ),
            Submission(
                widget_id=widget_a1.id,
                data={"email": "visitor3@test.com", "name": "Visitor Three"},
                ip_address="77.88.55.60",
                geo_country="Russia",
                geo_city="Moscow",
                geo_region="Moscow",
                created_at=now,
            ),
        ]
        for sub in submissions:
            session.add(sub)

        await session.commit()
        print("✅ Seed data created successfully!")
        print(f"   Users: alice@example.com / bob@example.com (password: password123)")
        print(f"   Widgets: {widget_a1.id}, {widget_a2.id}, {widget_b1.id}")
        print(f"   Submissions: {len(submissions)} sample submissions")


if __name__ == "__main__":
    asyncio.run(seed())
