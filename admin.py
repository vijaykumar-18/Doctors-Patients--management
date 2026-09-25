# ============================================================
# CREATE ADMIN USER
# ============================================================

from getpass import getpass

from main import (
    Base,
    SessionLocal,
    engine,
    User,
    hash_password
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# CREATE ADMIN FUNCTION
# ============================================================

def main():

    print()
    print("===================================")
    print("       CREATE ADMIN ACCOUNT")
    print("===================================")
    print()

    name = input(
        "Admin name: "
    ).strip()

    email = input(
        "Admin email: "
    ).strip()

    password = getpass(
        "Admin password: "
    )
    db = SessionLocal()

    try:


        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:

            print()
            print(
                "ERROR: A user with this email already exists."
            )

            return

        admin = User(
            name=name,
            email=email,
            password_hash=hash_password(
                password
            ),
            role="admin",
            is_active=True
        )

        db.add(admin)

        db.commit()

        print()
        print("===================================")
        print("Admin account created successfully!")
        print("===================================")
        print()
        print(f"Name: {name}")
        print(f"Email: {email}")
        print("Role: admin")
        print()

    finally:

        db.close()


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()
