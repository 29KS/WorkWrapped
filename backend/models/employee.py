from pydantic import BaseModel
from typing import Optional, List


class Employee(BaseModel):
    uid: str
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    fatherName: Optional[str] = None
    address: Optional[str] = None
    college: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[str] = None
    graduation_year: Optional[int] = None
    roll_no: Optional[str] = None
    education: Optional[str] = None
    role: Optional[str] = None
    position: Optional[str] = None
    domain: Optional[str] = None
    department: Optional[str] = None
    workMode: Optional[str] = None
    internshipType: Optional[str] = None
    internshipDurationMonths: Optional[int] = None
    joinDate: Optional[str] = None
    offerLetterRef: Optional[str] = None
    reportingTo: Optional[str] = None
    status: Optional[str] = None
    ndaSigned: Optional[bool] = None
    ndaSignedAt: Optional[str] = None
    assessmentScore: Optional[int] = None
    assessmentTimeTakenSec: Optional[int] = None
    assessmentFeedback: Optional[str] = None
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    summary: Optional[str] = None