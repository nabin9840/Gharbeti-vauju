"""
Setup script for Room Rental System
Run this after installing dependencies to set up the database and admin account
"""

from app import create_app, db
from app.models import User, Room
from datetime import datetime, timedelta

def setup_database():
    """Initialize the database and create tables"""
    app = create_app()

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")

        admin = User.query.filter_by(role='admin').first()
        if admin:
            print("✓ Admin account already exists!")
            return

        print("\n--- Creating Admin Account ---")
        name = input("Enter admin name: ").strip()
        email = input("Enter admin email: ").strip()
        password = input("Enter admin password: ").strip()

        if name and email and password:
            admin = User(
                name=name,
                email=email,
                role='admin'
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f"\n✓ Admin account created successfully!")
            print(f"  Email: {email}")
            print(f"  Role: admin")
        else:
            print("✗ Admin creation cancelled - missing information")

       
        create_sample = input("\nCreate sample data? (y/n): ").strip().lower()
        if create_sample == 'y':
            create_sample_data()

def create_sample_data():
    """Create sample users and rooms for testing"""
    app = create_app()

    with app.app_context():
        print("\nCreating sample data...")

        owner = User(
            name="John Owner",
            email="owner@example.com",
            role='owner'
        )
        owner.set_password("password123")
        db.session.add(owner)
        db.session.commit()

        viewer = User(
            name="Jane Renter",
            email="renter@example.com",
            role='viewer'
        )
        viewer.set_password("password123")
        db.session.add(viewer)
        db.session.commit()

        rooms_data = [
            {
                'title': 'Cozy Single Room in Downtown',
                'location': 'Mumbai, Maharashtra',
                'rent_price': 8000,
                'room_type': 'single',
                'description': 'A comfortable single room in the heart of the city with all amenities.',
                'status': 'approved'
            },
            {
                'title': 'Spacious Apartment Near Metro',
                'location': 'Delhi, NCR',
                'rent_price': 15000,
                'room_type': 'apartment',
                'description': 'Modern apartment with 2 bedrooms, fully furnished and near metro station.',
                'status': 'approved'
            },
            {
                'title': 'Shared Room for Students',
                'location': 'Pune, Maharashtra',
                'rent_price': 5000,
                'room_type': 'shared',
                'description': 'Affordable shared accommodation perfect for students.',
                'status': 'approved'
            },
            {
                'title': 'Luxury Studio in Tech Park Area',
                'location': 'Bangalore, Karnataka',
                'rent_price': 20000,
                'room_type': 'studio',
                'description': 'Premium studio apartment with modern amenities and 24/7 security.',
                'status': 'pending'
            }
        ]

        for room_data in rooms_data:
            room = Room(
                owner_id=owner.id,
                title=room_data['title'],
                location=room_data['location'],
                rent_price=room_data['rent_price'],
                room_type=room_data['room_type'],
                description=room_data['description'],
                image_filename='default_room.jpg',
                available_from=datetime.now().date(),
                available_to=(datetime.now() + timedelta(days=365)).date(),
                status=room_data['status']
            )
            db.session.add(room)

        db.session.commit()

        print("✓ Sample data created successfully!")
        print("\nSample Accounts Created:")
        print("  Owner: owner@example.com / password123")
        print("  Renter: renter@example.com / password123")
        print("\n4 sample rooms created (3 approved, 1 pending)")

if __name__ == '__main__':
    print("=" * 50)
    print("Room Rental System - Setup")
    print("=" * 50)
    print()

    try:
        setup_database()
        print("\n" + "=" * 50)
        print("Setup completed successfully!")
        print("Run 'python run.py' to start the application")
        print("=" * 50)
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        print("Please check your configuration and try again.")
