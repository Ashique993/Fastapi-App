from models import UserVisit
from sqlmodel import Session

def create_visit(session: Session, browser: str, os: str):
    visit = UserVisit(browser=browser, os=os)
    session.add(visit)
    session.commit()
    session.refresh(visit)
    return visit
