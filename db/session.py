from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from db.base import engine

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
