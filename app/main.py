from datetime import datetime, UTC, timedelta

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.models import get_session, Fixture, Location

application = FastAPI()


class DriveNow(BaseModel):
    answer: bool
    location: str
    start_time: datetime
    sport: str
    home_team: str


@application.get("/drive_now")
async def drive_now(location: str, session: Session = Depends(get_session)) -> DriveNow:
    fixture = session.exec(
        select(Fixture)
        .join(Location)
        .where(
            (Location.id == Fixture.location_id) & (Location.name == location)
        )
        .order_by(Fixture.start_time.asc())
    ).first()

    if not fixture:
        raise HTTPException(status_code=404)

    if fixture.start_time < datetime.now(UTC) + timedelta(hours=4):
        answer = False
    else:
        answer = True

    return DriveNow(
        answer=answer,
        location=fixture.location.name,
        start_time=fixture.start_time.isoformat(),
        sport=fixture.sport,
        home_team=fixture.home_team,
    )
