from contextlib import contextmanager
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./data.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session() -> Session:
    with Session(engine) as session:
        yield session

