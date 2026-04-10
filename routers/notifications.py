from fastapi import APIRouter, Query
from pathlib import Path
from .file_reader import read_file
import json
from warnings import warn
import re, string

router = APIRouter()

@router.get("/notifications")
def get_notifications(sites: list[str] = Query([])):
    notif_dir = Path('data/')

    notifications = []

    # drop anything that doesn't match the pattern for safety
    pattern = re.compile(r'^[a-zA-Z0-9_.-]+$')
    safe_sites = dict.fromkeys(s for s in sites if pattern.match(s))

    for site in sites:

        file_path = notif_dir/f"{site}_notifications.json"
        file_contents = read_file(file_path, 'json')
        if file_contents is not None:
            notifications += file_contents

    return notifications
