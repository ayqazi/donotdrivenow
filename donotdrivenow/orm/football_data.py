from sqlalchemy.orm import Mapped, mapped_column

from donotdrivenow.orm import Base


class FootballDataFixturesRaw(Base):
    __tablename__ = "football_data_fixtures_raw"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
