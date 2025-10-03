from typing import Optional, List
from datetime import datetime, timedelta
from sqlmodel import Session, select, func
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
    """Create and persist a UserVisit record with duplicate prevention."""

    # Check for recent duplicate visits (within 5 minutes)
    if ip_address and user_agent:
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        existing_visit = session.exec(
            select(UserVisit)
            .where(UserVisit.ip_address == ip_address)
            .where(UserVisit.user_agent == user_agent)
            .where(UserVisit.visit_datetime > five_minutes_ago)
        ).first()

        if existing_visit:
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
    """Fetch the most recent visit records."""
    statement = select(UserVisit).order_by(UserVisit.visit_datetime.desc()).limit(limit)
    return session.exec(statement).all()


def get_unique_users_stats(session: Session):
    """Get unique users with their statistics"""
    statement = select(
        UserVisit.ip_address,
        UserVisit.browser,
        UserVisit.os,
        func.max(UserVisit.visit_datetime).label("last_visit"),
        func.count(UserVisit.id).label("visit_count"),
    ).group_by(UserVisit.ip_address, UserVisit.browser, UserVisit.os)

    results = session.exec(statement).all()

    return [
        {
            "ip_address": result[0],
            "browser": result[1],
            "os": result[2],
            "last_visit": result[3].isoformat() if result[3] else None,
            "visit_count": result[4],
        }
        for result in results
    ]


def get_browser_statistics(session: Session):
    """Get statistics by browser type"""
    total_visits = session.exec(select(func.count(UserVisit.id))).one()

    statement = select(
        UserVisit.browser, func.count(UserVisit.id).label("count")
    ).group_by(UserVisit.browser)

    results = session.exec(statement).all()

    return [
        {
            "browser": result[0],
            "count": result[1],
            "percentage": (
                round((result[1] / total_visits) * 100, 2) if total_visits > 0 else 0
            ),
        }
        for result in results
    ]


def get_visits_by_ip(session: Session, ip_address: str) -> List[UserVisit]:
    """Get all visits from a specific IP address"""
    statement = (
        select(UserVisit)
        .where(UserVisit.ip_address == ip_address)
        .order_by(UserVisit.visit_datetime.desc())
    )
    return session.exec(statement).all()
