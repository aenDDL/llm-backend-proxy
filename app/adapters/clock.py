from datetime import UTC, date, datetime


class Clock:
    def now(self) -> date:
        return datetime.now(tz=UTC).date()
