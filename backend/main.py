from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from models import UserVisit
from database import get_session
import platform

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session: Session = Depends(get_session)):
    user_agent = request.headers.get("user-agent")
    client_host = request.client.host
    os_name = platform.system()

    # Save visit details in DB
    visit = UserVisit(browser=user_agent, os=os_name, ip=client_host)
    session.add(visit)
    session.commit()
