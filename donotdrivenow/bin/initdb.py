#!/usr/bin/env python3

from donotdrivenow import boot
from donotdrivenow.orm import Base, DataSource, Grab


def run():
    engine = boot()

    print(["Used models:",
           DataSource,
           Grab])

    Base.metadata.create_all(engine)


if __name__ == "__main__":
    run()
