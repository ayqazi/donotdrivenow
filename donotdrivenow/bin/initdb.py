#!/usr/bin/env python3

from donotdrivenow import boot
from donotdrivenow.orm import Base
from donotdrivenow.orm.data import raw

if __name__ == "__main__":
    engine = boot()

    print(["Used models:",
           raw.DataSource,
           raw.Grab])

    Base.metadata.create_all(engine)
