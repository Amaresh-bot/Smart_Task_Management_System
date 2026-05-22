from app import create_app
from app.extensions import db
from app.models import User, Task

app = create_app()

def initialize_database():
    print(" * Connecting to database and creating tables...")
    try:
        with app.app_context():
            db.create_all()
        print(" * Database tables successfully created!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        print("Make sure your PostgreSQL server is running and the credentials in .env are correct.")

if __name__ == "__main__":
    initialize_database()
