from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.product_family import ProductFamilyCreate, ProductFamilyRead
from app.services.product_family_service import ProductFamilyService

router = APIRouter(prefix="/product-families", tags=["product-families"])


@router.post("", response_model=ProductFamilyRead, status_code=status.HTTP_201_CREATED)
def create_product_family(
    payload: ProductFamilyCreate,
    session: Session = Depends(get_db_session),
) -> ProductFamilyRead:
    service = ProductFamilyService(session)
    family = service.create_product_family(payload)
    return ProductFamilyRead.model_validate(family)


@router.get("", response_model=list[ProductFamilyRead])
def list_product_families(
    session: Session = Depends(get_db_session),
) -> list[ProductFamilyRead]:
    service = ProductFamilyService(session)
    families = service.list_product_families()
    return [ProductFamilyRead.model_validate(family) for family in families]


@router.get("/{family_id}", response_model=ProductFamilyRead)
def get_product_family(
    family_id: int,
    session: Session = Depends(get_db_session),
) -> ProductFamilyRead:
    service = ProductFamilyService(session)
    family = service.get_product_family(family_id)
    return ProductFamilyRead.model_validate(family)