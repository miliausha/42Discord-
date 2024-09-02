from sqlalchemy.orm import Session
from app.db.database import engine


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()