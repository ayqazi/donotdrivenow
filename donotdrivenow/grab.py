import hashlib
import sys

import requests
from sqlalchemy import select

from donotdrivenow import util
from donotdrivenow.orm import DataSource, Grab


def grab_simple_source(name, url, content_type, session):
    with session.begin():
        source = session.execute(select(DataSource).where(DataSource.name == name)).scalar()
        now = util.now()

        if source is None:
            source = DataSource(name=name, url=url)
            session.add(source)
            session.flush()

        grab = session.scalar(select(Grab).where(Grab.data_source_id == source.id)
                              .order_by(Grab.grabbed.desc()).limit(1))
        if (grab is not None and
                grab.grabbed.year == now.year and
                grab.grabbed.month == now.month and
                grab.grabbed.day == now.day):
            print(f"{source.name}: already grabbed today", file=sys.stderr)
            return grab

        print(f"{source.name}: initiating grab", file=sys.stderr)
        rawdata = requests.get(source.url).text

        sha3_256sum = hashlib.sha3_256(bytes(rawdata, 'UTF-8')).hexdigest()

        if grab is not None and sha3_256sum == grab.sha3_256sum:
            print(f"{source.name}: last grab has not changed", file=sys.stderr)
            return grab

        grab = Grab(data_source_id=source.id,
                    grabbed=now,
                    data=rawdata,
                    content_type=content_type,
                    sha3_256sum=sha3_256sum)
        session.add(grab)
        session.flush()
        session.commit()

    return grab
