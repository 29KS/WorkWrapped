import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

try:
    from google import genai
    from google.genai.errors import ServerError, ClientError
    client = genai.Client(api_key=API_KEY)
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False


def generate_employee_summary(employee: dict, prediction: dict) -> str:
    prompt = f"""
You are an HR analytics assistant.
Generate an engaging "Employee Wrapped" summary.

Employee Details
Name: {employee.get("name")}
Department: {employee.get("department")}
Position: {employee.get("position")}
Role: {employee.get("role")}
Join Date: {employee.get("joinDate")}

Attendance
Present Days: {employee.get("presentDays")}
Leave Days: {employee.get("leaveDays")}
Late Arrivals: {employee.get("lateArrivals")}
Average Working Hours: {employee.get("avgHours")}

Task Statistics
Completed Tasks: {employee.get("doneTasks")}
Pending Tasks: {employee.get("pendingTasks")}
Overdue Tasks: {employee.get("overdueTasks")}
On-Time Completions: {employee.get("onTimeCompletions")}
Total Estimated Hours: {employee.get("totalEstimatedHours")}
Total Actual Hours: {employee.get("totalActualHours")}

AI Predictions
Burnout Risk: {prediction.get("burnoutRisk")}
Work Personality: {prediction.get("workPersonality")}
Performance Score: {prediction.get("performanceScore")}
Performance Grade: {prediction.get("performanceGrade")}

Instructions
- Write around 120-150 words.
- Make it sound like Spotify Wrapped — engaging and fun.
- Mention strengths and achievements.
- Mention one area of improvement.
- Keep the tone motivating and professional.
- Do NOT use bullet points.
- Return only the summary paragraph.
"""

    if not GEMINI_AVAILABLE:
        return _fallback_summary(employee, prediction)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip() if response.text else _fallback_summary(employee, prediction)

    except Exception as e:
        print("Gemini Error:", e)
        return _fallback_summary(employee, prediction)


def _fallback_summary(employee: dict, prediction: dict) -> str:
    name  = employee.get("name", "This employee")
    dept  = employee.get("department", "their department")
    score = prediction.get("performanceScore", "N/A")
    grade = prediction.get("performanceGrade", "")
    risk  = prediction.get("burnoutRisk", "Low")
    pers  = prediction.get("workPersonality", "Balanced Performer")
    done  = employee.get("doneTasks", 0)
    ontime = employee.get("onTimeCompletions", 0)

    return (
        f"{name} wrapped up an impressive stint in {dept}! "
        f"With a Performance Score of {score} (Grade {grade}), they completed {done} tasks "
        f"with {ontime} on-time deliveries — a true {pers}. "
        f"Attendance was consistent and working hours reflect strong dedication. "
        f"The predicted Burnout Risk is {risk}, so keeping up work-life balance "
        f"will be key going forward. Here's to an even stronger chapter ahead! 🚀"
    )