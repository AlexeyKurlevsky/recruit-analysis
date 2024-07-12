from dataclasses import dataclass


@dataclass
class ApplucantStatusResponse:
    status_id: int
    status_name: str


@dataclass
class ApplicantStatistic:
    status_id: int
    value: int


@dataclass
class ApplicantValueByStatus:
    status_id: int
    status_name: str
    current_value: int | None
    common_value: int | None
