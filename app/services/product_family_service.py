from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    AttributeDefinitionModel,
    AttributeOptionModel,
    AttributeType,
    ProductFamilyModel,
)
from app.domain.exceptions import ProductFamilyAlreadyExistsError, ProductFamilyNotFoundError
from app.schemas.product_family import ProductFamilyCreate


class ProductFamilyService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_product_family(self, payload: ProductFamilyCreate) -> ProductFamilyModel:
        existing = self.session.scalar(
            select(ProductFamilyModel).where(ProductFamilyModel.code == payload.code)
        )
        if existing:
            raise ProductFamilyAlreadyExistsError(
                f"Product family with code '{payload.code}' already exists."
            )

        family = ProductFamilyModel(
            code=payload.code,
            name=payload.name,
            description=payload.description,
            is_active=payload.is_active,
        )

        for attribute in payload.attributes:
            attribute_model = AttributeDefinitionModel(
                code=attribute.code,
                name=attribute.name,
                description=attribute.description,
                attribute_type=AttributeType(attribute.attribute_type.value),
                is_required=attribute.is_required,
                unit=attribute.unit,
                min_int=attribute.min_int,
                max_int=attribute.max_int,
                min_decimal=attribute.min_decimal,
                max_decimal=attribute.max_decimal,
            )

            for option in attribute.enum_options:
                attribute_model.enum_options.append(
                    AttributeOptionModel(
                        value=option.value,
                        label=option.label,
                        sort_order=option.sort_order,
                    )
                )

            family.attributes.append(attribute_model)

        self.session.add(family)
        self.session.commit()
        self.session.refresh(family)

        return self.get_product_family(family.id)

    def get_product_family(self, family_id: int) -> ProductFamilyModel:
        family = self.session.scalar(
            select(ProductFamilyModel)
            .options(
                selectinload(ProductFamilyModel.attributes).selectinload(
                    AttributeDefinitionModel.enum_options
                )
            )
            .where(ProductFamilyModel.id == family_id)
        )
        if not family:
            raise ProductFamilyNotFoundError(f"Product family with id '{family_id}' not found.")

        return family

    def list_product_families(self) -> list[ProductFamilyModel]:
        result = self.session.scalars(
            select(ProductFamilyModel).options(
                selectinload(ProductFamilyModel.attributes).selectinload(
                    AttributeDefinitionModel.enum_options
                )
            )
        )
        return list(result.all())