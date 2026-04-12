from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    AttributeDefinitionModel,
    ProductFamilyModel,
)


class ProductFamilyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, family_id: int) -> ProductFamilyModel | None:
        return self.session.scalar(
            select(ProductFamilyModel)
            .options(
                selectinload(ProductFamilyModel.attributes).selectinload(
                    AttributeDefinitionModel.enum_options
                ),
                selectinload(ProductFamilyModel.rules),
                selectinload(ProductFamilyModel.pricing_rules),
            )
            .where(ProductFamilyModel.id == family_id)
        )

    def get_by_code(self, code: str) -> ProductFamilyModel | None:
        return self.session.scalar(
            select(ProductFamilyModel).where(ProductFamilyModel.code == code)
        )

    def list_all(self) -> list[ProductFamilyModel]:
        result = self.session.scalars(
            select(ProductFamilyModel).options(
                selectinload(ProductFamilyModel.attributes).selectinload(
                    AttributeDefinitionModel.enum_options
                ),
                selectinload(ProductFamilyModel.rules),
                selectinload(ProductFamilyModel.pricing_rules),
            )
        )
        return list(result.all())

    def add(self, family: ProductFamilyModel) -> None:
        self.session.add(family)