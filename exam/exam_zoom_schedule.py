# ここで試したいこと
# スケジュール登録をまず試そう
# ストリーム設定は、YouTube Live側のAPIでストリームキーなど作れた時に

# requestsでやる

import os
import json
import requests

import dotenv
from pprint import pprint

dotenv.load_dotenv()
zoom_jwt_token = os.environ["ZOOM_JWT_TOKEN"]

API_ROOT = "https://api.zoom.us"

headers = {
    'authorization': f"Bearer {zoom_jwt_token}",
    'content-type': "application/json"
    }

# スケジュール一覧をみる
userid = "XpB0xoWMTX6f2uQ5pQAzgg"

res_meetings = requests.get(API_ROOT + f"/v2/users/{userid}/meetings" , headers=headers)
meetings = res_meetings.json()
pprint(meetings)

# スケジュール登録

# meetingの構造を作る

create_meeting_json_template = """
{
  "topic": "wip:apitest:",
  "type": "2",
  "start_time": "2021-09-10T10:00:00Z",
  "duration": "40",
  "timezone": "Asia/Tokyo",
  "agenda": "",
  "settings": {
    "host_video": "true",
    "participant_video": "true",
    "join_before_host": "true",
    "mute_upon_entry": "boolean",
    "watermark": "false",
    "audio": "voip",
    "auto_recording": "local",
    "enforce_login": "false"
  }
}
"""

create_meeting_json_template = """
{
  "topic": "wip:apitest:日本語テストです",
  "type": "2",
  "start_time": "2021-09-10T10:00:00Z",
  "duration": "45",
  "timezone": "Asia/Tokyo",
  "agenda": "",
  "settings": {
    "host_video": "true",
    "participant_video": "true",
    "join_before_host": "true",
    "watermark": "false",
    "audio": "voip",
    "auto_recording": "local",
    "enforce_login": "false"
  }
}
"""

# jsonをloadsしておく

create_meeting_json = json.loads(create_meeting_json_template)

print(json.dumps(create_meeting_json))

res_add_meeting = requests.post(API_ROOT + f"/v2/users/me/meetings" ,
                    headers=headers,
                    data=json.dumps(create_meeting_json))
print(res_add_meeting)

added_meeting = res_add_meeting.json()
pprint(added_meeting)

