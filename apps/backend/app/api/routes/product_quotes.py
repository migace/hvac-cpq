from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.product_quote import ProductQuoteCreate, ProductQuoteRead
from app.services.product_quote_service import ProductQuoteService

router = APIRouter(prefix="/product-quotes", tags=["product-quotes"])


@router.post("", response_model=ProductQuoteRead, status_code=status.HTTP_201_CREATED)
def create_product_quote(
    payload: ProductQuoteCreate,
    session: Session = Depends(get_db_session),
) -> ProductQuoteRead:
    service = ProductQuoteService(session)
    quote = service.create_quote(payload.product_configuration_id)
    return ProductQuoteRead.model_validate(quote)


@router.get("", response_model=list[ProductQuoteRead])
def list_product_quotes(
    session: Session = Depends(get_db_session),
) -> list[ProductQuoteRead]:
    service = ProductQuoteService(session)
    quotes = service.list_quotes()
    return [ProductQuoteRead.model_validate(item) for item in quotes]


@router.get("/{quote_id}", response_model=ProductQuoteRead)
def get_product_quote(
    quote_id: int,
    session: Session = Depends(get_db_session),
) -> ProductQuoteRead:
    service = ProductQuoteService(session)
    quote = service.get_quote(quote_id)
    return ProductQuoteRead.model_validate(quote)