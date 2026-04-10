import time as t
from fastapi import APIRouter, Query
from pathlib import Path
from .file_reader import read_file
from . import timetable_helpers as ttbl
import json
from warnings import warn
import re, string

# ttbl is an abbreviation for timetable

router = APIRouter()

@router.get("/timetable-for-date")
def get_timetable_for_date(unix_time: float = Query(default_factory=t.time)):
    return ttbl.get_timetable_for_date(unix_time)

@router.get("/is-school-day")
def get_if_day_school_day(unix_time: float = Query(default_factory=t.time)):
    return ttbl.get_timetable_for_date(unix_time, True)
