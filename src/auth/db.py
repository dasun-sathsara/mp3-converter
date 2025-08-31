from collections.abc import Iterator

from sqlmodel import Session, create_engine

from config import settings

engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
