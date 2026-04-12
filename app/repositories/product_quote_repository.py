from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ProductQuoteModel


class ProductQuoteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, quote_id: int) -> ProductQuoteModel | None:
        return self.session.scalar(
            select(ProductQuoteModel).where(ProductQuoteModel.id == quote_id)
        )

    def list_all(self) -> list[ProductQuoteModel]:
        result = self.session.scalars(
            select(ProductQuoteModel).order_by(ProductQuoteModel.id.desc())
        )
        return list(result.all())

    def add(self, quote: ProductQuoteModel) -> None:
        self.session.add(quote)