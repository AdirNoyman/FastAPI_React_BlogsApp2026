from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass

# Returns a new database session for each request (each request gets her own session). The 'with' statement ensures that the session is properly closed after the request is processed, even if an error occurs. This is important for preventing database connection leaks and ensuring that resources are managed efficiently.
def get_db():
    with SessionLocal() as db:
        yield db


