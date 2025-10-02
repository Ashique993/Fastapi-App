from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from database import get_session
from crud import create_visit, get_recent_visits
from sqlmodel import Session
from datetime import datetime
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="User Visit Tracker API",
    description="API for tracking website visits and user information",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def detect_browser(user_agent: str) -> str:
    """Enhanced browser detection"""
    if "Edg/" in user_agent:
        return "Microsoft Edge"
    elif "OPR/" in user_agent or "Opera" in user_agent:
        return "Opera"
    elif (
        "Chrome/" in user_agent
        and "Edg/" not in user_agent
        and "OPR/" not in user_agent
    ):
        return "Google Chrome"
    elif "Firefox/" in user_agent:
        return "Mozilla Firefox"
    elif "Safari/" in user_agent and "Chrome/" not in user_agent:
        return "Safari"
    else:
        return "Unknown Browser"


def detect_os(user_agent: str) -> str:
    """Enhanced OS detection"""
    if "Android" in user_agent:
        return "Android"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        return "iOS"
    elif "Windows NT" in user_agent:
        return "Windows"
    elif "Mac OS X" in user_agent:
        return "macOS"
    elif "Linux" in user_agent and "Android" not in user_agent:
        return "Linux"
    else:
        return "Unknown OS"


def get_client_info(request: Request) -> tuple[str, str]:
    """Extract client information from request safely"""
    user_agent = request.headers.get("user-agent", "Unknown")
    client_ip = "Unknown"
    if request.client:
        client_ip = request.client.host

    # Real IP headers
    if xff := request.headers.get("X-Forwarded-For"):
        client_ip = xff.split(",")[0].strip()
    elif real_ip := request.headers.get("X-Real-IP"):
        client_ip = real_ip

    return user_agent, client_ip


@app.post("/api/track")
async def track_visit(request: Request, session: Session = Depends(get_session)):
    """API endpoint to track visits from frontend"""
    try:
        data = await request.json()
        user_agent, client_ip = get_client_info(request)

        # Create visit record with frontend data
        visit = create_visit(
            session=session,
            browser=data.get("browser", "Unknown"),
            os=data.get("os", "Unknown"),
            visit_datetime=datetime.now(),
            screen_resolution=data.get("screen_resolution"),
            user_agent=user_agent,
            url=data.get("url", str(request.url)),
            ip_address=client_ip,
        )

        logger.info(f"Visit tracked: ID {visit.id} from {client_ip}")

        return {
            "status": "success",
            "visit_id": visit.id,
            "message": "Visit tracked successfully",
            "data": {
                "id": visit.id,
                "browser": visit.browser,
                "os": visit.os,
                "screen_resolution": visit.screen_resolution,
                "ip_address": visit.ip_address,
                "timestamp": visit.timestamp.isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Error tracking visit: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/visits")
async def get_visits(limit: int = 10, session: Session = Depends(get_session)):
    """Get recent visits"""
    try:
        visits = get_recent_visits(session, limit)
        return {
            "total": len(visits),
            "visits": [
                {
                    "id": v.id,
                    "timestamp": v.timestamp.isoformat(),
                    "browser": v.browser,
                    "os": v.os,
                    "screen_resolution": v.screen_resolution,
                    "ip_address": v.ip_address,
                    "url": v.url,
                }
                for v in visits
            ],
        }
    except Exception as e:
        logger.error(f"Error fetching visits: {e}")
        return {"error": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "user-visit-tracker",
        "timestamp": datetime.now().isoformat(),
    }
