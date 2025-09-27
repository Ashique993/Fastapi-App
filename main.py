from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from database import get_session
from crud import create_visit
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_client_info(request: Request):
    """Extract client information from request"""
    user_agent = request.headers.get("user-agent", "Unknown")
    client_ip = request.client.host

    # Get real IP if behind proxy
    if forwarded_for := request.headers.get("X-Forwarded-For"):
        client_ip = forwarded_for.split(",")[0].strip()
    elif real_ip := request.headers.get("X-Real-IP"):
        client_ip = real_ip

    return user_agent, client_ip


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session: Session = Depends(get_session)):
     """Serve the HTML page and track the visit automatically"""
    
    try:
        # Extract client information
        user_agent, client_ip = get_client_info(request)
        
        # Simple browser detection from user-agent
        browser = "Unknown"
        if "Chrome" in user_agent and "Edg" not in user_agent:
            browser = "Chrome"
        elif "Firefox" in user_agent:
            browser = "Firefox"
        elif "Safari" in user_agent and "Chrome" not in user_agent:
            browser = "Safari"
        elif "Edg" in user_agent:
            browser = "Edge"
        
        # Simple OS detection from user-agent
        os = "Unknown"
        if "Android" in user_agent:
            os = "Android"
        elif "iPhone" in user_agent or "iPad" in user_agent:
            os = "iOS"
        elif "Windows" in user_agent:
            os = "Windows"
        elif "Mac OS X" in user_agent:
            os = "macOS"
        elif "Linux" in user_agent:
            os = "Linux"
        
        # Create visit record
        visit = create_visit(
            session=session,
            browser=browser,
            os=os,
            visit_datetime=datetime.now(),
            screen_resolution=None,  # Can't detect server-side
            user_agent=user_agent,
            url=str(request.url),
            ip_address=client_ip
        )
        
        logger.info(f"Visit tracked: ID {visit.id} from {client_ip} using {browser} on {os}")
        
    except Exception as e:
        logger.error(f"Error tracking visit: {str(e)}")
        visit = None
    
    # Return HTML page with tracking confirmation
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hi</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                text-align: center;
            }}
            .visit-info {{
                background-color: #f0f8ff;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 15px;
                margin-top: 20px;
                font-size: 14px;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <h1>Hi</h1>
        <div class="visit-info">
            {'✅ Visit tracked successfully!' if visit else '❌ Error tracking visit'}
            {f'<br>Visit ID: {visit.id}' if visit else ''}
            <br>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/visits/")
async def get_visits(limit: int = 10, session: Session = Depends(get_session)):
    """Get recent visits for monitoring"""
    try:
        from sqlmodel import select
        from models import UserVisit
        
        statement = select(UserVisit).order_by(UserVisit.timestamp.desc()).limit(limit)
        visits = session.exec(statement).all()
        
        return {
            "total": len(visits),
            "visits": [
                {
                    "id": visit.id,
                    "timestamp": visit.timestamp.isoformat(),
                    "visit_datetime": visit.visit_datetime.isoformat() if visit.visit_datetime else None,
                    "browser": visit.browser,
                    "os": visit.os,
                    "ip_address": visit.ip_address,
                    "url": visit.url
                }
                for visit in visits
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching visits: {str(e)}")
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "user-visit-tracker",
        "timestamp": datetime.now().isoformat()
    }