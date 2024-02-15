#!/usr/bin/env python

import sys

from sqlalchemy import *
from sqlalchemy.orm import *

import donotdrivenow
import donotdrivenow.util as util
from donotdrivenow.orm import *


def get_session():
    return Session(donotdrivenow.boot())


session = get_session()
