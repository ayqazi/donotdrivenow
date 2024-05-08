from datetime import datetime, UTC, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app.main import application
from app.models import Fixture, Location, init_db, get_session


@pytest.fixture
def session():
    engine = init_db("postgresql+psycopg2://localhost/donotdrivenow_test", create_all=True)
    with Session(engine) as session:
        session.execute(text("TRUNCATE fixture RESTART IDENTITY CASCADE"))
        session.execute(text("TRUNCATE location RESTART IDENTITY CASCADE"))
        yield session
        session.commit()


@pytest.fixture(name="client")
def client_fixture(session: Session):
    application.dependency_overrides[get_session] = lambda: session
    client = TestClient(application)
    yield client
    application.dependency_overrides.clear()


@pytest.fixture
def test_location() -> Location:
    return Location(name="Test City")


@pytest.fixture
def test_fixture(test_location: Location) -> Fixture:
    return Fixture(sport="football",
                   home_team="Team 1",
                   away_team="Team 2",
                   location=test_location,
                   start_time=datetime.now(UTC) + timedelta(hours=3, minutes=59))


@pytest.fixture
def build_response(test_fixture: Fixture):
    def _f(overrides=None) -> dict:
        return {
            "location": "Test City",
            "start_time": test_fixture.start_time.isoformat(),
            "sport": "football",
            "home_team": "Team 1",
        } | (overrides or {})

    return _f


def test_valid_request_with_future_fixture_answer_yes(session: Session, test_fixture: Fixture,
                                                      client: TestClient, build_response):
    test_fixture.start_time = datetime.now(UTC) + timedelta(hours=4, minutes=1)
    with session:
        session.add(test_fixture)
        session.commit()
        session.refresh(test_fixture)

    response = client.get("/drive_now?location=Test City")
    assert response.status_code == 200
    assert response.json() == build_response({"answer": True})


def test_valid_request_with_future_fixture_answer_no(session: Session, test_fixture: Fixture,
                                                     client: TestClient, build_response):
    with session:
        session.add(test_fixture)
        session.commit()
        session.refresh(test_fixture)

    response = client.get("/drive_now?location=Test City")
    assert response.status_code == 200
    assert response.json() == build_response({"answer": False})


def test_valid_request_with_multiple_fixtures_uses_earliest_future_fixture(session: Session, test_fixture: Fixture,
                                                                           client: TestClient, build_response):
    with session:
        session.add(
            Fixture(sport="football",
                    home_team="Team 3",
                    away_team="Team 4",
                    location=test_fixture.location,
                    start_time=datetime.now(UTC) + timedelta(hours=5, minutes=0))
        )
        session.add(test_fixture)
        session.commit()
        session.refresh(test_fixture)

    response = client.get("/drive_now?location=Test City")
    assert response.status_code == 200
    assert response.json() == build_response({"answer": False})


def test_invalid_request(client: TestClient):
    response = client.get("/drive_now")
    assert response.status_code == 422


def test_location_not_found(client: TestClient):
    response = client.get("/drive_now?location=Nonexistent Town")
    assert response.status_code == 404
