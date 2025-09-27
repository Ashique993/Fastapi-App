from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class UserVisit(SQLModel, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Server timestamp when record is created",
    )
    browser: str = Field(description="Browser name and version")
    os: str = Field(description="Operating system information")
