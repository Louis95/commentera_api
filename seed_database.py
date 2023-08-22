import csv
import uuid

from sqlalchemy import cast
from sqlalchemy.orm import Session
from modules.database.models import User, Badge
from modules.utilities.database import SessionLocal
from sqlalchemy.dialects.postgresql import UUID


def seed_user_and_badge_tables_from_csv():
    Session = SessionLocal
    session = Session()
    # Check if any user already exists in the database
    existing_user_count = session.query(User).count()

    if existing_user_count > 0:
        print("Users already exist in the database. Skipping seeding.")
        return

    with open('customers.csv', mode="r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            customer_id = row["customer_id"]
            status = row["status"]

            # Generate a new UUID for the user
            user_id = uuid.uuid4()

            badge_names = [badge for badge in row.values() if badge and badge != customer_id and badge != status]

            # Check if the user already exists in the database
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(id=user_id, customer_id=customer_id)
                session.add(user)
                session.commit()
                print(f"New user added: {user.id}")

            # Get the current badges for the user
            existing_badges = user.badges

            # Handle the case where the user already has two badges
            if len(existing_badges) >= 2:
                # Remove one badge and add the new badge
                badge_to_remove = existing_badges.pop(0)  # Remove the first badge
                session.delete(badge_to_remove)

            # Add or update badges for the user
            for badge_name in badge_names:
                badge = next((b for b in existing_badges if b.badge_name == badge_name), None)
                if badge:
                    badge.badge_name = badge_name
                else:
                    new_badge = Badge(badge_name=badge_name, user=user)
                    session.add(new_badge)
                    print(f"New badge added: {new_badge} to user: {new_badge.user_id}")

            session.commit()


# Usage example:
# Assuming db_session is a valid SQLAlchemy session

seed_user_and_badge_tables_from_csv()
