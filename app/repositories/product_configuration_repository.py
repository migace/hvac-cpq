from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    AttributeValueModel,
    ProductConfigurationModel,
    ProductFamilyModel,
)


class ProductConfigurationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, configuration_id: int) -> ProductConfigurationModel | None:
        return self.session.scalar(
            select(ProductConfigurationModel)
            .options(
                selectinload(ProductConfigurationModel.product_family).selectinload(
                    ProductFamilyModel.attributes
                ),
                selectinload(ProductConfigurationModel.values).selectinload(
                    AttributeValueModel.attribute_definition
                ),
                selectinload(ProductConfigurationModel.quotes),
            )
            .where(ProductConfigurationModel.id == configuration_id)
        )

    def add(self, configuration: ProductConfigurationModel) -> None:
        self.session.add(configuration)