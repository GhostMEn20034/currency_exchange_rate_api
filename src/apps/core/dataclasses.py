from dataclasses import dataclass
from datetime import date


@dataclass
class DateRange:
    start_date: date
    end_date: date
