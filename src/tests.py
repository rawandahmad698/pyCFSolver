import datetime
import json
import threading
import time

import requests

def _post_json(json_data):
    url = "http://localhost:8192/v1"

    payload = json.dumps(json_data)
    headers = {
        'Content-Type': 'application/json'
    }
    return requests.request("POST", url, headers=headers, data=payload)


def test_session_create():
    session_count = 3
    for i in range(session_count):
        cmd = {
            "cmd": "sessions.create",
            "session": "1",
            "url": "http://www.soleretriever.com",
            "maxTimeout": 60000,
            "headless": True
        }
        threading.Thread(target=_post_json, args=(cmd,)).start()

    print(">> Created", session_count, "sessions.")

def test_browser_request():
    cmd = {
      "cmd": "request.get",
      "url": "http://www.google.com",
      "session": "1",
      "maxTimeout": 60000,
      "headless": True,
      "returnOnlyCookies": True
    }
    response = _post_json(cmd)
    print(response.text)

def test_ttl():
    time_now = datetime.datetime.now()
    cmd = {
      "cmd": "request.get",
      "session": "1",
      "url":"http://www.google.com",
      "session_ttl_minutes": 1,
      "maxTimeout": 60000,
      "headless": True,
      "returnOnlyCookies": True
    }
    while True:
        threading.Thread(target=_post_json, args=(cmd,)).start()
        time.sleep(10)
        print(">>", (datetime.datetime.now() - time_now).seconds, "seconds elapsed")
        if (datetime.datetime.now() - time_now).seconds > 80:
            break

if __name__ == "__main__":
    test_session_create()
    test_browser_request()
    test_ttl()