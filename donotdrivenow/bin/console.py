#!/usr/bin/env python

import code

from sqlalchemy.orm import *

import donotdrivenow


def get_session():
    session = Session(donotdrivenow.boot())
    return session


if __name__ == "__main__":
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()
