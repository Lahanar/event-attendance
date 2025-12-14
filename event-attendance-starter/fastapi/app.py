from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from uuid import uuid4
from datetime import datetime
from pathlib import Path as FsPath

app = FastAPI(title="Event Attendance API (FastAPI)")

# CORS (อนุญาตทั้งหมดเพื่อเดโม)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# เสิร์ฟหน้าเว็บที่ /web และ redirect จาก / ไป /web/
web_dir = FsPath(__file__).resolve().parent.parent / "web"
if web_dir.exists():
    app.mount("/web", StaticFiles(directory=str(web_dir), html=True), name="web")

@app.get("/")
def root():
    return RedirectResponse(url="/web/")

# ตัวอย่าง event
EVENTS = {"e1": {"id": "e1", "name": "Sample Event"}}

# In-memory stores
ATTENDEE_BY_ID = {}
ATTENDEE_BY_EMAIL = {}  # (eventId, email) -> attendee

class AttendeeCreate(BaseModel):
    name: str
    email: EmailStr
    ticketType: str | None = "standard"

def norm_email(e: str) -> str:
    return e.strip().lower()

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def error_response(status_code: int, error: str, message: str, details: dict | None = None):
    body = {"error": error, "message": message}
    if details:
        body["details"] = details
    return JSONResponse(status_code=status_code, content=body)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/events/{eventId}/attendees", status_code=201)
def create_attendee(eventId: str = Path(...), payload: AttendeeCreate = ...):
    if eventId not in EVENTS:
        return error_response(404, "NotFound", "event not found")

    name = payload.name.strip()
    if not name:
        return error_response(400, "BadRequest", "name is required")

    email = norm_email(payload.email)
    key = (eventId, email)
    if key in ATTENDEE_BY_EMAIL:
        return error_response(409, "Conflict", "attendee already exists for this event")

    att_id = str(uuid4())
    ts = now_iso()
    attendee = {
        "id": att_id,
        "eventId": eventId,
        "name": name,
        "email": email,
        "ticketType": payload.ticketType or "standard",
        "status": "registered",
        "checkInAt": None,
        "createdAt": ts,
        "updatedAt": ts
    }
    ATTENDEE_BY_EMAIL[key] = attendee
    ATTENDEE_BY_ID[att_id] = attendee
    return attendee
