from sqlmodel import create_engine, Session

from backend.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)


def get_db():
    with Session(engine) as session:
        yield session
