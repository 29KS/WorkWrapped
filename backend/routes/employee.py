from fastapi import APIRouter, HTTPException
from backend.database import employee_collection

router = APIRouter(prefix="/employees", tags=["Employee"])


@router.get("/{uid}")
async def get_employee(uid: str):
    employee = await employee_collection.find_one({"uid": uid}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.get("/")
async def list_employees():
    employees = []
    async for emp in employee_collection.find({}, {"_id": 0}):
        employees.append(emp)
    return employees