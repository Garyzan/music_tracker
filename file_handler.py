import json
import os

import mbdb_interface

from datetime import date

ID_TO_NAMES = {}
with open("id_to_names.json", "r") as f:
    ID_TO_NAMES = json.load(f)

def add_artists(uid: int, artist_ids: list[str]) -> None:
    filepath = f"tracks/{uid}.json"
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            tracking: dict = json.load(f)
    else:
        tracking = {}
    for artist_id in artist_ids:
        if not artist_id in tracking.keys():
            tracking[artist_id] = date.today().strftime('%Y-%m-%d')
    with open(filepath, 'w') as f:
        json.dump(tracking, f)

def remove_artists(uid: int, artist_ids: list[str]) -> None:
    filepath = f"tracks/{uid}.json"
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            tracking: dict = json.load(f)

        for artist_id in artist_ids:
            if artist_id in tracking.keys():
                del tracking[artist_id]

        if len(tracking.keys()) == 0:
            os.remove(filepath)
        else:
            with open(filepath, 'w') as f:
                json.dump(tracking, f)

def remove_all_artists(uid: int) -> None:
    filepath = f"tracks/{uid}.json"
    if os.path.isfile(filepath):
            os.remove(filepath)

def get_artists(uid: int) -> list[str]:
    filepath = f"tracks/{uid}.json"
    if not os.path.isfile(filepath):
        return []
    with open(filepath, 'r') as f:
        tracking: dict = json.load(f)
    return tracking.keys()

def get_last_date(uid: str, artist_id: str) -> str | None:
    filepath = f"tracks/{uid}.json"
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            tracking: dict = json.load(f)
        return tracking[artist_id]

def update_last_date(uid: str, artist_id: str, new_date: str = None) -> None:
    if new_date == None:
        new_date = date.today().strftime('%Y-%m-%d')
    filepath = f"tracks/{uid}.json"
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            tracking: dict = json.load(f)
        if artist_id in tracking.keys():
            with open(filepath, 'w') as f:
                tracking[artist_id] = new_date
                json.dump(tracking, f)

def get_name(artist_id: str) -> str:
    if not artist_id in ID_TO_NAMES.keys():
        ID_TO_NAMES[artist_id] = mbdb_interface.get_artist_name(artist_id)
        with open("id_to_names.json", "w") as f:
            json.dump(ID_TO_NAMES, f)
    return ID_TO_NAMES[artist_id]
