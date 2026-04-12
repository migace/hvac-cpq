from sqlalchemy import text
from sqlalchemy.orm import Session


class QuoteNumberService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def generate(self) -> str:
        result = self.session.execute(text("SELECT nextval('quote_number_seq')"))
        seq_val = result.scalar()
        return f"Q-{seq_val:08d}"
