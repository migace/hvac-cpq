from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger

logger = get_logger()


def commit_and_refresh(session: Session, entity) -> None:
    try:
        session.commit()
        session.refresh(entity)
    except SQLAlchemyError as exc:
        session.rollback()
        logger.exception(
            "database_commit_failed",
            error=str(exc),
            entity_type=type(entity).__name__,
        )
        raise