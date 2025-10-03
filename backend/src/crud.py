from typing import Optional, List
from datetime import datetime, timedelta
from sqlmodel import Session, select
from models import UserVisit


def create_visit(
    session: Session,
    browser: str,
    os: str,
    visit_datetime: Optional[datetime] = None,
    screen_resolution: Optional[str] = None,
    user_agent: Optional[str] = None,
    url: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> UserVisit:
    """
    Create and persist a UserVisit record.
    """

    # Check for recent duplicate visits (within 5 minutes)
    if ip_address and user_agent:
        time_dutation = datetime.now() - timedelta(minutes=1)
        existing_visit = session.exec(
            select(UserVisit)
            .where(UserVisit.ip_address == ip_address)
            .where(UserVisit.user_agent == user_agent)
            .where(UserVisit.visit_datetime > time_dutation)
        ).first()

        if existing_visit:
            # Return existing visit instead of creating duplicate
            return existing_visit

    visit = UserVisit(
        browser=browser,
        os=os,
        visit_datetime=visit_datetime,
        screen_resolution=screen_resolution,
        user_agent=user_agent,
        url=url,
        ip_address=ip_address,
    )
    session.add(visit)
    session.commit()
    session.refresh(visit)
    return visit


def get_recent_visits(session: Session, limit: int = 10) -> List[UserVisit]:
    """
    Fetch the most recent visit records up to `limit`.
    """
    statement = select(UserVisit).order_by(UserVisit.timestamp.desc()).limit(limit)
    return session.exec(statement).all()


def get_visit_by_id(session: Session, visit_id: int) -> Optional[UserVisit]:
    """
    Retrieve a single visit by its primary key.
    """
    return session.get(UserVisit, visit_id)


def get_visit_count(session: Session) -> int:
    """
    Count total visits in the database.
    """
    statement = select(UserVisit)
    return session.exec(statement).count()
