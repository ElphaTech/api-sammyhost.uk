'''
A collection of helper functions to aid in returning timetables and related stuff.
Timetables should be lists of events (dictionaries) in the following format:
    {
        "name": "name of event",
        "all_day": False,
        "start_time": {unix timestamp of start},
        "end_time": {unix timestamp of end}
    }
'''

import time as t
from pathlib import Path
from .file_reader import read_file
import json
from warnings import warn
import re, string

TTBL_DIR = Path('data/')

def get_start_of_day(unix_time:float):
    unix_time = t.localtime(unix_time)
    start = t.struct_time((
        unix_time.tm_year, unix_time.tm_mon, unix_time.tm_mday,
        0, 0, 0, 0, 0, unix_time.tm_isdst
    ))
    return t.mktime(start)

def all_day_event(name, unix_date):
    '''
    Takes in a name and date (unix of somewhere on that day).
    Returns a list with a dict of the single day long event.
    '''
    start = get_start_of_day(unix_date)
    return [{
        "name": name,
        "all_day": True,
        "start_time": start,
        "end_time": start+86400
    }]


def get_timetable_for_date(unix_time:float=t.time(), check_school_day:bool=False) -> list:

    local_time = t.localtime(unix_time)
    day_of_week = t.strftime("%A", local_time)
    day_events = []

    # Check if weekend (no overrides or multiday or anything on weekends)
    if day_of_week in ['Saturday', 'Sunday']:
        if check_school_day:
            return False
        return all_day_event("Have a good weekend!", unix_time)

    # 1. Load timetable_overrides.json
    ttbl_multiday = read_file(TTBL_DIR/'timetable_multiday.json', 'json')
    ttbl_overrides = read_file(TTBL_DIR/'timetable_overrides.json', 'json')

    # 2. Check if today in multiday
    for event in ttbl_multiday:
        #{
            #"name": "Term 1/2 Holidays",
            #"school_open": false,
            #"start_date": "04/04/2026",
            #"end_date": "19/04/2026"
        #}
        # where md is multiday
        md_unix_start = t.mktime(t.strptime(event['start_date'], "%d/%m/%Y"))
        md_unix_end = t.mktime(t.strptime(event['end_date'], "%d/%m/%Y")) + 3600*24
        if md_unix_start <= unix_time < md_unix_end:
            if check_school_day:
                return event['school_open']
            return all_day_event(event['name'], unix_time)

    date = t.strftime("%d/%m/%Y", t.localtime(unix_time))
    if date in ttbl_overrides.keys() and len(ttbl_overrides[date]['events']) >= 1:
        overrides = ttbl_overrides[date]

        if check_school_day:
            return overrides['school_open']
        
        if overrides['events'][0].get('repeating', False):
            event_list = []
            start_of_day = get_start_of_day(unix_time)
            item_start_time = overrides['events'][0].get('start_time', 300)+start_of_day
            end_time = overrides['events'][0].get('end_time', 300)+start_of_day
            item_interval = overrides['events'][0].get('interval', 300)
            item_name_template = overrides['events'][0].get('item_names', 300)
            item_count = 1
            while True and item_start_time+item_interval <= end_time:
                event_list.append({
                    "name": item_name_template.format(item_count),
                    "all_day": False,
                    "start_time": item_start_time,
                    "end_time": item_start_time + item_interval
                })
                item_count += 1
                item_start_time += item_interval
            return event_list


        if overrides['events'][0].get('all_day', False):
            return all_day_event(overrides['events'][0]['name'], unix_time)

        if overrides.get('replace'):
            return overrides['events']

        # TODO: LAST CASE : USE SKL TTBL BUT CHANGE IDK HOW

    # Return normal school day timetable
    if check_school_day:
        return True

    ttbl_skl_day = read_file(TTBL_DIR/'school_timetable.json', 'json')[day_of_week]
    for i in range(len(ttbl_skl_day)):
        ttbl_skl_day[i]['start_time'] += get_start_of_day(unix_time)
        ttbl_skl_day[i]['end_time'] += get_start_of_day(unix_time)
    return ttbl_skl_day

