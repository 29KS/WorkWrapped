from pydantic import BaseModel


class WorkingHours(BaseModel):
    average_hours: float
    total_hours: float


class CheckInOut(BaseModel):
    earliest_checkin: str
    latest_checkout: str


class AttendanceOut(BaseModel):
    attendance_percentage: float

    present_days: int
    leave_days: int
    late_arrivals: int

    working_hours: WorkingHours

    checkin_checkout: CheckInOut

    short_days: int
    missed_checkouts: int
    idle_warning_days: int
    geo_out_of_range_days: int