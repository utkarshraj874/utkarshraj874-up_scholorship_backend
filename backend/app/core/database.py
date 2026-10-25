from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from backend.app.core.config import DATABASE_URL
#This creates a connection engine to your database (PostgreSQL, MySQL, etc.).
#It doesn’t open a connection immediately, but sets up the configuration so SQLAlchemy knows how to talk to the database.
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine # says ( which database to use ) Use interview_simulator database.
)
#sesssionmaker(), This is a factory function that generates new Session objects.
#A Session is the main way you interact with the database: you use it to query, insert, update, and delete rows.
#By defining SessionLocal, you can easily create sessions later with SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
