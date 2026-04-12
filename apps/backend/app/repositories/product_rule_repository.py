from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ProductRuleModel


class ProductRuleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_family(self, family_id: int) -> list[ProductRuleModel]:
        result = self.session.scalars(
            select(ProductRuleModel)
            .where(ProductRuleModel.product_family_id == family_id)
            .order_by(ProductRuleModel.id.asc())
        )
        return list(result.all())

    def add(self, rule: ProductRuleModel) -> None:
        self.session.add(rule)