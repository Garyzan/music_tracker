import json
import os

from datetime import date


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
    
def update_last_date(uid: str, artist_id: str) -> None:
    filepath = f"tracks/{uid}.json"
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            tracking: dict = json.load(f)
        if artist_id in tracking.keys():
            with open(filepath, 'w') as f:
                tracking[artist_id] = date.today().strftime('%Y-%m-%d')
                json.dump(tracking, f)
