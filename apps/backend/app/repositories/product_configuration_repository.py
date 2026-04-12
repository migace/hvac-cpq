from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    AttributeDefinitionModel,
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
                selectinload(ProductConfigurationModel.product_family).options(
                    selectinload(ProductFamilyModel.attributes).selectinload(
                        AttributeDefinitionModel.enum_options
                    ),
                    selectinload(ProductFamilyModel.pricing_rules),
                ),
                selectinload(ProductConfigurationModel.values).selectinload(
                    AttributeValueModel.attribute_definition
                ),
                selectinload(ProductConfigurationModel.quotes),
            )
            .where(ProductConfigurationModel.id == configuration_id)
        )

    def list_all(self) -> list[ProductConfigurationModel]:
        result = self.session.scalars(
            select(ProductConfigurationModel)
            .options(
                selectinload(ProductConfigurationModel.product_family),
                selectinload(ProductConfigurationModel.values),
            )
            .order_by(ProductConfigurationModel.id.desc())
        )
        return list(result.all())

    def add(self, configuration: ProductConfigurationModel) -> None:
        self.session.add(configuration)