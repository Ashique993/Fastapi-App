from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from database import get_session
from crud import *
from sqlmodel import Session
from datetime import datetime
import logging
import pytz

IST = pytz.timezone("Asia/Kolkata")


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
    allow_origins=["http://localhost:8080", "http://192.168.1.100:8080"],
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
    """Track user visit"""
    try:
        data = await request.json()
        user_agent, client_ip = get_client_info(request)
        ist_now = datetime.now(IST)

        visit = create_visit(
            session=session,
            browser=data.get("browser", "Unknown"),
            os=data.get("os", "Unknown"),
            visit_datetime=ist_now,
            screen_resolution=data.get("screen_resolution"),
            user_agent=user_agent,
            url=data.get("url", str(request.url)),
            ip_address=client_ip,
        )

        return {
            "status": "success",
            "visit_id": visit.id,
            "message": "Visit tracked successfully",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/visits")
async def get_visits(limit: int = 10, session: Session = Depends(get_session)):
    """Get all recent visits"""
    visits = get_recent_visits(session, limit)
    return {
        "total": len(visits),
        "visits": [
            {
                "id": v.id,
                "timestamp": v.visit_datetime.isoformat() if v.visit_datetime else None,
                "browser": v.browser,
                "os": v.os,
                "screen_resolution": v.screen_resolution,
                "ip_address": v.ip_address,
                "url": v.url,
            }
            for v in visits
        ],
    }


@app.get("/api/analytics/unique-users")
async def get_unique_users(session: Session = Depends(get_session)):
    """Get unique users by IP and browser combination"""
    unique_users = get_unique_users_stats(session)
    return {"unique_users": unique_users}


@app.get("/api/analytics/browser-stats")
async def get_browser_stats(session: Session = Depends(get_session)):
    """Get visitor statistics by browser"""
    browser_stats = get_browser_statistics(session)
    return {"browser_stats": browser_stats}


@app.get("/api/analytics/user-sessions/{ip_address}")
async def get_user_sessions(ip_address: str, session: Session = Depends(get_session)):
    """Get all visits from a specific user/IP"""
    user_visits = get_visits_by_ip(session, ip_address)
    return {
        "ip_address": ip_address,
        "total_visits": len(user_visits),
        "visits": [
            {
                "id": v.id,
                "timestamp": v.visit_datetime.isoformat(),
                "browser": v.browser,
                "os": v.os,
                "url": v.url,
            }
            for v in user_visits
        ],
    }


@app.get("/api/database-viewer")
async def database_viewer():
    """Serve database viewer page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Viewer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
            .stat-card { border: 1px solid #ddd; padding: 15px; border-radius: 8px; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .refresh-btn { background: #007bff; color: white; padding: 10px 15px; border: none; cursor: pointer; margin: 5px; }
        </style>
    </head>
    <body>
        <h1>📊 Database Analytics Viewer</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>🌐 Browser Statistics</h3>
                <div id="browser-stats">Loading...</div>
            </div>
            
            <div class="stat-card">
                <h3>👥 Unique Users</h3>
                <div id="unique-users">Loading...</div>
            </div>
        </div>
        
        <div class="stat-card">
            <h3>📋 All Visits Database</h3>
            <button class="refresh-btn" onclick="loadAllData()">🔄 Refresh All Data</button>
            <div id="all-visits">Loading...</div>
        </div>

        <script>
            const API_BASE = 'http://localhost:3000/api';
            
            async function loadBrowserStats() {
                try {
                    const response = await fetch(`${API_BASE}/analytics/browser-stats`);
                    const data = await response.json();
                    
                    let html = '<table><tr><th>Browser</th><th>Count</th><th>Percentage</th></tr>';
                    data.browser_stats.forEach(stat => {
                        html += `<tr><td>${stat.browser}</td><td>${stat.count}</td><td>${stat.percentage}%</td></tr>`;
                    });
                    html += '</table>';
                    
                    document.getElementById('browser-stats').innerHTML = html;
                } catch (error) {
                    document.getElementById('browser-stats').innerHTML = '❌ Error loading data';
                }
            }
            
            async function loadUniqueUsers() {
                try {
                    const response = await fetch(`${API_BASE}/analytics/unique-users`);
                    const data = await response.json();
                    
                    let html = '<table><tr><th>IP Address</th><th>Browser</th><th>OS</th><th>Last Visit</th><th>Visit Count</th></tr>';
                    data.unique_users.forEach(user => {
                        html += `<tr>
                            <td><a href="#" onclick="loadUserSessions('${user.ip_address}')">${user.ip_address}</a></td>
                            <td>${user.browser}</td>
                            <td>${user.os}</td>
                            <td>${new Date(user.last_visit).toLocaleString()}</td>
                            <td>${user.visit_count}</td>
                        </tr>`;
                    });
                    html += '</table>';
                    
                    document.getElementById('unique-users').innerHTML = html;
                } catch (error) {
                    document.getElementById('unique-users').innerHTML = '❌ Error loading data';
                }
            }
            
            async function loadAllVisits() {
                try {
                    const response = await fetch(`${API_BASE}/visits?limit=50`);
                    const data = await response.json();
                    
                    let html = '<table><tr><th>ID</th><th>Timestamp</th><th>IP</th><th>Browser</th><th>OS</th><th>Screen</th></tr>';
                    data.visits.forEach(visit => {
                        html += `<tr>
                            <td>${visit.id}</td>
                            <td>${new Date(visit.timestamp).toLocaleString()}</td>
                            <td>${visit.ip_address}</td>
                            <td>${visit.browser}</td>
                            <td>${visit.os}</td>
                            <td>${visit.screen_resolution}</td>
                        </tr>`;
                    });
                    html += '</table>';
                    
                    document.getElementById('all-visits').innerHTML = html;
                } catch (error) {
                    document.getElementById('all-visits').innerHTML = '❌ Error loading data';
                }
            }
            
            async function loadUserSessions(ip) {
                try {
                    const response = await fetch(`${API_BASE}/analytics/user-sessions/${ip}`);
                    const data = await response.json();
                    
                    alert(`User ${ip} has ${data.total_visits} total visits. Check console for details.`);
                    console.log('User Sessions:', data);
                } catch (error) {
                    alert('Error loading user sessions');
                }
            }
            
            function loadAllData() {
                loadBrowserStats();
                loadUniqueUsers();  
                loadAllVisits();
            }
            
            // Load data when page loads
            window.addEventListener('load', loadAllData);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
