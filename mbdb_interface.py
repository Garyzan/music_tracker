import requests

from datetime import date
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=1, period=1.1)
def mbdb_get(req_string):
    return requests.get(req_string)

def get_releases_since(artist_id: str, startdate: str) -> requests.Response:
    today = date.today().strftime('%Y-%m-%d')
    req_string = f"https://musicbrainz.org/ws/2/release?fmt=json&query=arid:{artist_id}%20AND%20date:[{startdate}%20TO%20{today}]"
    return mbdb_get(req_string)

def get_artist_name(artist_id: str) -> str:
    req_string = f"https://musicbrainz.org/ws/2/artist/{artist_id}?fmt=json"
    resp = mbdb_get(req_string)
    if resp.status_code != 200:
        return ""
    return resp.json()['name']