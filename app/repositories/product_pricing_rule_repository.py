from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ProductPricingRuleModel


class ProductPricingRuleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_family(self, family_id: int) -> list[ProductPricingRuleModel]:
        result = self.session.scalars(
            select(ProductPricingRuleModel)
            .where(ProductPricingRuleModel.product_family_id == family_id)
            .order_by(ProductPricingRuleModel.id.asc())
        )
        return list(result.all())

    def add(self, rule: ProductPricingRuleModel) -> None:
        self.session.add(rule)