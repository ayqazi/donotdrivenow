from datetime import datetime, UTC, timedelta

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class DriveNow(BaseModel):
    answer: bool
    location: str
    earliest_start_time: datetime
    sport: str
    venue: str


@app.get("/drive_now")
async def drive_now(location: str) -> DriveNow:
    start_time = datetime.now(UTC) + timedelta(hours=2.5)
    return DriveNow(
        answer=False,
        location=location,
        earliest_start_time=start_time.isoformat(),
        sport="caber tossing",
        venue="CRAZY PLACE",
    )
