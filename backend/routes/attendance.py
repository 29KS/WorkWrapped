from fastapi import APIRouter, HTTPException
from database import employee_collection
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

router = APIRouter(prefix="/employees", tags=["Attendance"])

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


def calculate_attendance_percentage(present_days, total_days):
    if total_days == 0:
        return 0
    return round((present_days / total_days) * 100, 2)


@router.get("/{uid}/attendance")
async def get_attendance(uid: str):
    employee = await employee_collection.find_one({"uid": uid})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # ✅ query raw_attendance, not task_performance
    attendance = await db["raw_attendance"].find_one({"uid": uid}, {"_id": 0})
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance data not found")

    attendance_percentage = calculate_attendance_percentage(
        attendance.get("presentDays", 0),
        attendance.get("totalDays", 0)
    )

    return {
        "attendance_percentage": attendance_percentage,
        "present_days": attendance.get("presentDays", 0),
        "leave_days": attendance.get("leaveDays", 0),
        "late_arrivals": attendance.get("lateArrivals", 0),
        "working_hours": {
            "average_hours": attendance.get("avgHours", 0),
            "total_hours": attendance.get("totalHours", 0)
        },
        "checkin_checkout": {
            "earliest_checkin": attendance.get("earliestCheckIn", "N/A"),
            "latest_checkout": attendance.get("latestCheckOut", "N/A")
        },
        "short_days": attendance.get("shortDays", 0),
        "missed_checkouts": attendance.get("missedCheckouts", 0),
        "idle_warning_days": attendance.get("idleWarningDays", 0),
        "geo_out_of_range_days": attendance.get("geoOutOfRangeDays", 0)
    }