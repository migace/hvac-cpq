from datetime import datetime, UTC


class QuoteNumberService:
    def generate(self) -> str:
        now = datetime.now(UTC)
        return f"Q-{now.strftime('%Y%m%d%H%M%S%f')}"