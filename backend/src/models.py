from sqlmodel import SQLModel, Field, Index
from datetime import datetime
from typing import Optional


class UserVisit(SQLModel, table=True):

    __table_args__ = (
        # Add unique constraint to prevent duplicates within 1 minute
        Index("idx_unique_visit", "ip_address", "user_agent", "visit_datetime"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    visit_datetime: Optional[datetime] = Field(
        default=None, description="Client-side timestamp when page was visited"
    )
    browser: str = Field(index=True, description="Browser name (e.g., Chrome, Firefox)")
    os: str = Field(
        index=True, description="Operating system name (e.g., Android, iOS)"
    )
    screen_resolution: Optional[str] = Field(
        default=None, description="Screen resolution if available"
    )
    user_agent: Optional[str] = Field(
        default=None, description="Full user-agent string"
    )
    url: Optional[str] = Field(default=None, description="URL requested")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")


# class UserVisit2(SQLModel, table=True):

#     id: Optional[int] = Field(default=None, primary_key=True)


# class UserVisit3(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     os: str = Field(
#         index=True, description="Operating system name (e.g., Android, iOS)"
#     )
