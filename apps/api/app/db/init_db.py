from sqlalchemy.orm import Session

from app.db.session import engine
from app.models.base import Base


def init_db() -> None:
    """Create all tables for local/dev startup."""
    Base.metadata.create_all(bind=engine)


def seed_db(_db: Session) -> None:
    """Placeholder for future data seeding."""
    return None
