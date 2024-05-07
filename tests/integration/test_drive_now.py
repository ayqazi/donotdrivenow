from datetime import datetime, UTC, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import application
from app.models import Fixture, engine


@pytest.fixture
def client():
    return TestClient(application)


@pytest.fixture(autouse=True)
def fixture_record():
    with Session(engine) as session:
        session.add(Fixture(sport="football",
                            home_team="My City",
                            away_team="Their City",
                            start_time=datetime.now(UTC) + timedelta(hours=2)))

        session.commit()


def test_valid_request(client: TestClient):
    response = client.get("/drive_now?location=fake_town")
    assert response.status_code == 200
    assert response.json().keys() == {"answer", "location", "earliest_start_time", "sport", "venue"}


def test_invalid_request(client: TestClient):
    response = client.get("/drive_now")
    assert response.status_code == 422


def test_location_not_found(client: TestClient):
    response = client.get("/drive_now?location=fake_town")
    assert response.status_code == 404
