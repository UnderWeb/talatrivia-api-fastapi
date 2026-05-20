# app/scripts/seed_admin.py
"""Seed initial admin user (idempotent)."""

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User


def seed_admin() -> None:
    db: Session = SessionLocal()

    try:
        existing_admin = db.query(User).filter(User.role == "admin").first()

        if existing_admin:
            print("Admin already exists. Skipping seed.")
            return

        admin_user = User(
            name="Admin",
            email="admin@talatrivia.com",
            hashed_password=hash_password("admin1234"),
            role="admin",
        )

        db.add(admin_user)
        db.commit()

        print("Admin user created successfully.")

    finally:
        db.close()


def main() -> None:
    seed_admin()


if __name__ == "__main__":
    main()
