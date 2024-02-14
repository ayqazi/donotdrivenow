#!/usr/bin/env python

import sys

from sqlalchemy import *
from sqlalchemy.orm import *

import donotdrivenow
import donotdrivenow.util as util
from donotdrivenow.orm import *


def get_session():
    return Session(donotdrivenow.boot())


# if __name__ == "__main__":
#     variables = globals().copy()
#     variables.update(locals())
#     shell = code.InteractiveConsole(variables)
#     shell.interact()
