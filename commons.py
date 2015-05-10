#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from re import match
def convert_time(time):
    regex = '([0-9]{4})/([0-9]{2})/([0-9]{2}) ([0-9]{2}):([0-9]{2})'
    m = match(regex, time).groups()
    return datetime(int(m[0]), int(m[1]), int(m[2]), int(m[3]), int(m[4]), 0)
