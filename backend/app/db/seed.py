"""Database seed script for development data.

Run with: python -m app.db.seed
"""
import asyncio
import sys
from datetime import datetime, timedelta, timezone, time
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.session import async_session_factory
from app.models import (
    Organization,
    Branch,
    User,
    Customer,
    Vehicle,
    Job,
    Script,
    Campaign,
    CampaignTarget,
    Call,
    Appointment,
)
from app.models.enums import (
    UserRole,
    CampaignStatus,
    CampaignType,
    CallDirection,
    CallStatus,
    CallOutcome,
    AppointmentStatus,
    JobCategory,
)


async def seed_database() -> None:
    """Seed the database with development data."""
    async with async_session_factory() as session:
        # Check if already seeded
        from sqlalchemy import select
        result = await session.execute(select(Organization).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping.")
            return

        print("Seeding database...")

        # Create organization
        org = Organization(
            id=uuid4(),
            name="Demo Auto Group",
            slug="demo-auto-group",
            settings={
                "elevenlabs_agent_id": "demo-agent-id",
                "default_timezone": "America/New_York",
            },
            subscription_tier="professional",
        )
        session.add(org)
        await session.flush()
        print(f"Created organization: {org.name}")

        # Create branches
        branches = [
            Branch(
                id=uuid4(),
                org_id=org.id,
                name="Downtown Service Center",
                address="123 Main Street, New York, NY 10001",
                phone="+12125551234",
                timezone="America/New_York",
                business_hours={
                    "monday": {"open": "08:00", "close": "18:00"},
                    "tuesday": {"open": "08:00", "close": "18:00"},
                    "wednesday": {"open": "08:00", "close": "18:00"},
                    "thursday": {"open": "08:00", "close": "18:00"},
                    "friday": {"open": "08:00", "close": "18:00"},
                    "saturday": {"open": "09:00", "close": "14:00"},
                    "sunday": {"open": None, "close": None},
                },
            ),
            Branch(
                id=uuid4(),
                org_id=org.id,
                name="Uptown Sales",
                address="456 Broadway, New York, NY 10012",
                phone="+12125555678",
                timezone="America/New_York",
                business_hours={
                    "monday": {"open": "09:00", "close": "20:00"},
                    "tuesday": {"open": "09:00", "close": "20:00"},
                    "wednesday": {"open": "09:00", "close": "20:00"},
                    "thursday": {"open": "09:00", "close": "20:00"},
                    "friday": {"open": "09:00", "close": "20:00"},
                    "saturday": {"open": "10:00", "close": "18:00"},
                    "sunday": {"open": "11:00", "close": "17:00"},
                },
            ),
        ]
        for branch in branches:
            session.add(branch)
        await session.flush()
        print(f"Created {len(branches)} branches")

        # Create users
        users = [
            User(
                id=uuid4(),
                org_id=org.id,
                branch_id=branches[0].id,
                email="admin@demo-auto.com",
                password_hash=get_password_hash("admin123"),
                full_name="Admin User",
                role=UserRole.admin,
            ),
            User(
                id=uuid4(),
                org_id=org.id,
                branch_id=branches[0].id,
                email="manager@demo-auto.com",
                password_hash=get_password_hash("manager123"),
                full_name="Service Manager",
                role=UserRole.manager,
            ),
            User(
                id=uuid4(),
                org_id=org.id,
                branch_id=branches[1].id,
                email="agent@demo-auto.com",
                password_hash=get_password_hash("agent123"),
                full_name="Sales Agent",
                role=UserRole.agent,
            ),
        ]
        for user in users:
            session.add(user)
        await session.flush()
        print(f"Created {len(users)} users")

        # Create jobs
        jobs = [
            Job(
                id=uuid4(),
                org_id=org.id,
                code="OIL_CHANGE",
                name="Oil Change",
                description="Standard oil change service",
                category=JobCategory.service,
                estimated_duration_minutes=30,
                base_price=Decimal("49.99"),
            ),
            Job(
                id=uuid4(),
                org_id=org.id,
                code="BRAKE_INSP",
                name="Brake Inspection",
                description="Full brake system inspection",
                category=JobCategory.service,
                estimated_duration_minutes=45,
                base_price=Decimal("29.99"),
            ),
            Job(
                id=uuid4(),
                org_id=org.id,
                code="TIRE_ROTATION",
                name="Tire Rotation",
                description="Four-wheel tire rotation",
                category=JobCategory.service,
                estimated_duration_minutes=30,
                base_price=Decimal("24.99"),
            ),
            Job(
                id=uuid4(),
                org_id=org.id,
                code="30K_SERVICE",
                name="30,000 Mile Service",
                description="Comprehensive 30K mile maintenance",
                category=JobCategory.service,
                estimated_duration_minutes=180,
                base_price=Decimal("299.99"),
            ),
        ]
        for job in jobs:
            session.add(job)
        await session.flush()
        print(f"Created {len(jobs)} jobs")

        # Create script
        script = Script(
            id=uuid4(),
            org_id=org.id,
            name="Service Reminder Script",
            description="Standard script for service reminder calls",
            voice_id="EXAVITQu4vr4xnSDxMaL",  # Example ElevenLabs voice ID
            first_message="Hi {{customer_name}}, this is Sarah from Demo Auto Group. I'm calling about your {{vehicle_year}} {{vehicle_make}} {{vehicle_model}}. According to our records, it's time for your {{service_name}}. Do you have a moment to discuss scheduling?",
            system_prompt="""You are Sarah, a friendly and professional service advisor at Demo Auto Group. Your goal is to help customers schedule their vehicle maintenance appointments.

Key behaviors:
- Be warm and personable, but respect the customer's time
- Explain the importance of the service without being pushy
- Offer flexible scheduling options
- If the customer asks about pricing, provide the base price and mention any current promotions
- If the customer is not interested, politely thank them and end the call
- If the customer requests not to be called again, acknowledge and add them to the do-not-call list

Available appointment times: Monday-Friday 8am-5pm, Saturday 9am-1pm
Current promotion: 10% off for appointments booked this week""",
            model_id="gpt-4o-mini",
            temperature=Decimal("0.7"),
            max_duration_seconds=300,
            language="en",
            variables=[
                {"name": "customer_name", "type": "string", "required": True},
                {"name": "vehicle_year", "type": "string", "required": True},
                {"name": "vehicle_make", "type": "string", "required": True},
                {"name": "vehicle_model", "type": "string", "required": True},
                {"name": "service_name", "type": "string", "required": True},
            ],
            created_by_id=users[0].id,
        )
        session.add(script)
        await session.flush()
        print(f"Created script: {script.name}")

        # Create customers with vehicles
        customers_data = [
            {
                "first_name": "John",
                "last_name": "Smith",
                "phone": "+12125551001",
                "email": "john.smith@email.com",
                "vehicles": [
                    {"year": 2021, "make": "Toyota", "model": "Camry", "mileage": 28500},
                ],
            },
            {
                "first_name": "Emily",
                "last_name": "Johnson",
                "phone": "+12125551002",
                "email": "emily.j@email.com",
                "vehicles": [
                    {"year": 2020, "make": "Honda", "model": "Accord", "mileage": 35200},
                    {"year": 2019, "make": "Honda", "model": "CR-V", "mileage": 42100},
                ],
            },
            {
                "first_name": "Michael",
                "last_name": "Brown",
                "phone": "+12125551003",
                "email": "mbrown@email.com",
                "vehicles": [
                    {"year": 2022, "make": "Ford", "model": "F-150", "mileage": 18900},
                ],
            },
            {
                "first_name": "Sarah",
                "last_name": "Davis",
                "phone": "+12125551004",
                "email": "sdavis@email.com",
                "vehicles": [
                    {"year": 2021, "make": "Chevrolet", "model": "Equinox", "mileage": 31000},
                ],
            },
            {
                "first_name": "David",
                "last_name": "Wilson",
                "phone": "+12125551005",
                "email": "dwilson@email.com",
                "vehicles": [
                    {"year": 2020, "make": "Nissan", "model": "Altima", "mileage": 39500},
                ],
            },
        ]

        customers = []
        vehicles = []
        for data in customers_data:
            customer = Customer(
                id=uuid4(),
                org_id=org.id,
                branch_id=branches[0].id,
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone=data["phone"],
                email=data["email"],
            )
            session.add(customer)
            customers.append(customer)

            for v_data in data["vehicles"]:
                vehicle = Vehicle(
                    id=uuid4(),
                    customer_id=customer.id,
                    year=v_data["year"],
                    make=v_data["make"],
                    model=v_data["model"],
                    mileage=v_data["mileage"],
                    is_primary=len(vehicles) == 0,
                )
                session.add(vehicle)
                vehicles.append(vehicle)

        await session.flush()
        print(f"Created {len(customers)} customers with {len(vehicles)} vehicles")

        # Create campaign
        campaign = Campaign(
            id=uuid4(),
            org_id=org.id,
            branch_id=branches[0].id,
            script_id=script.id,
            name="January Service Reminders",
            description="Monthly service reminder campaign for customers due for oil change",
            type=CampaignType.service_reminder,
            status=CampaignStatus.active,
            scheduled_start=datetime.now(timezone.utc) - timedelta(days=2),
            actual_start=datetime.now(timezone.utc) - timedelta(days=2),
            calling_hours_start=time(9, 0),
            calling_hours_end=time(17, 0),
            calling_days=[1, 2, 3, 4, 5],  # Monday-Friday
            max_attempts=3,
            target_count=5,
            completed_count=3,
            success_count=2,
            created_by_id=users[1].id,
        )
        session.add(campaign)
        await session.flush()
        print(f"Created campaign: {campaign.name}")

        # Create campaign targets and calls
        now = datetime.now(timezone.utc)
        call_data = [
            {
                "customer_idx": 0,
                "vehicle_idx": 0,
                "status": CallStatus.completed,
                "outcome": CallOutcome.appointment_booked,
                "duration": 145,
                "started_at": now - timedelta(days=2, hours=3),
            },
            {
                "customer_idx": 1,
                "vehicle_idx": 1,
                "status": CallStatus.completed,
                "outcome": CallOutcome.appointment_booked,
                "duration": 178,
                "started_at": now - timedelta(days=2, hours=2),
            },
            {
                "customer_idx": 2,
                "vehicle_idx": 2,
                "status": CallStatus.completed,
                "outcome": CallOutcome.callback_requested,
                "duration": 62,
                "started_at": now - timedelta(days=1, hours=4),
                "needs_attention": True,
                "attention_reason": "Customer requested callback at specific time",
            },
            {
                "customer_idx": 3,
                "vehicle_idx": 3,
                "status": CallStatus.no_answer,
                "outcome": CallOutcome.no_answer,
                "duration": 0,
                "started_at": now - timedelta(days=1, hours=2),
            },
            {
                "customer_idx": 4,
                "vehicle_idx": 4,
                "status": CallStatus.pending,
                "outcome": None,
                "duration": None,
                "started_at": None,
            },
        ]

        for idx, c_data in enumerate(call_data):
            customer = customers[c_data["customer_idx"]]
            vehicle = vehicles[c_data["vehicle_idx"]]

            target = CampaignTarget(
                id=uuid4(),
                campaign_id=campaign.id,
                customer_id=customer.id,
                vehicle_id=vehicle.id,
                job_id=jobs[0].id,  # Oil change
                is_completed=c_data["status"] == CallStatus.completed,
                outcome=c_data["outcome"],
                variables={
                    "customer_name": f"{customer.first_name} {customer.last_name}",
                    "vehicle_year": str(vehicle.year),
                    "vehicle_make": vehicle.make,
                    "vehicle_model": vehicle.model,
                    "service_name": "oil change",
                },
            )
            session.add(target)
            await session.flush()

            if c_data["started_at"]:
                ended_at = (
                    c_data["started_at"] + timedelta(seconds=c_data["duration"])
                    if c_data["duration"]
                    else None
                )
                call = Call(
                    id=uuid4(),
                    org_id=org.id,
                    branch_id=branches[0].id,
                    campaign_id=campaign.id,
                    campaign_target_id=target.id,
                    customer_id=customer.id,
                    elevenlabs_conversation_id=f"conv_{uuid4().hex[:8]}",
                    direction=CallDirection.outbound,
                    status=c_data["status"],
                    outcome=c_data["outcome"],
                    phone_number=customer.phone,
                    started_at=c_data["started_at"],
                    ended_at=ended_at,
                    duration_seconds=c_data["duration"],
                    needs_attention=c_data.get("needs_attention", False),
                    attention_reason=c_data.get("attention_reason"),
                    summary=f"Service reminder call to {customer.first_name} for {vehicle.year} {vehicle.make} {vehicle.model}",
                )
                session.add(call)

                # Create appointment for booked calls
                if c_data["outcome"] == CallOutcome.appointment_booked:
                    appt = Appointment(
                        id=uuid4(),
                        org_id=org.id,
                        branch_id=branches[0].id,
                        customer_id=customer.id,
                        vehicle_id=vehicle.id,
                        call_id=call.id,
                        job_id=jobs[0].id,
                        scheduled_at=now + timedelta(days=3 + idx),
                        estimated_duration_minutes=30,
                        status=AppointmentStatus.scheduled,
                        source="ai_call",
                        notes="Booked via AI voice agent",
                    )
                    session.add(appt)

        await session.flush()
        print("Created campaign targets and calls")

        await session.commit()
        print("\n✅ Database seeded successfully!")
        print("\nDemo credentials:")
        print("  Admin: admin@demo-auto.com / admin123")
        print("  Manager: manager@demo-auto.com / manager123")
        print("  Agent: agent@demo-auto.com / agent123")


async def main():
    """Main entry point."""
    try:
        await seed_database()
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
