from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.product_configuration import (
    AttributeValueRead,
    ProductConfigurationCreate,
    ProductConfigurationRead,
)
from app.services.product_configuration_service import ProductConfigurationService
from app.schemas.pricing import PricingResponse, PriceBreakdownItemRead

router = APIRouter(prefix="/product-configurations", tags=["product-configurations"])


def _extract_value(value_obj) -> str | int | float | bool | None:
    if value_obj.value_integer is not None:
        return value_obj.value_integer
    if value_obj.value_decimal is not None:
        return value_obj.value_decimal
    if value_obj.value_boolean is not None:
        return value_obj.value_boolean
    return value_obj.value_string


def _to_read_model(configuration) -> ProductConfigurationRead:
    return ProductConfigurationRead(
        id=configuration.id,
        product_family_id=configuration.product_family_id,
        name=configuration.name,
        status=configuration.status,
        values=[
            AttributeValueRead(
                attribute_code=value.attribute_definition.code,
                attribute_name=value.attribute_definition.name,
                attribute_type=value.attribute_definition.attribute_type.value,
                unit=value.attribute_definition.unit,
                value=_extract_value(value),
            )
            for value in configuration.values
        ],
    )


def _to_pricing_response(result) -> PricingResponse:
    return PricingResponse(
        currency=result.currency,
        base_price=result.base_price,
        surcharge_total=result.surcharge_total,
        total_price=result.total_price,
        breakdown=[
            PriceBreakdownItemRead(
                rule_name=item.rule_name,
                label=item.label,
                amount=item.amount,
            )
            for item in result.breakdown
        ],
    )


@router.post("", response_model=ProductConfigurationRead, status_code=status.HTTP_201_CREATED)
def create_product_configuration(
    payload: ProductConfigurationCreate,
    session: Session = Depends(get_db_session),
) -> ProductConfigurationRead:
    service = ProductConfigurationService(session)
    configuration = service.create_configuration(payload)
    return _to_read_model(configuration)


@router.get("/{configuration_id}", response_model=ProductConfigurationRead)
def get_product_configuration(
    configuration_id: int,
    session: Session = Depends(get_db_session),
) -> ProductConfigurationRead:
    service = ProductConfigurationService(session)
    configuration = service.get_configuration(configuration_id)
    return _to_read_model(configuration)


@router.post("/calculate-price", response_model=PricingResponse)
def calculate_product_configuration_price(
    payload: ProductConfigurationCreate,
    session: Session = Depends(get_db_session),
) -> PricingResponse:
    service = ProductConfigurationService(session)
    result = service.calculate_configuration_price(payload)
    return _to_pricing_response(result)