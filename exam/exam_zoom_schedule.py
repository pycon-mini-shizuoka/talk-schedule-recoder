# ここで試したいこと
# スケジュール登録をまず試そう
# ストリーム設定は、YouTube Live側のAPIでストリームキーなど作れた時に

# requestsでやる

import os
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
  "topic": "test meeting:ミーティングのタイトルかな？",
  "type": " 2",
  "start_time": "2021-08-20T10:00:00Z",
  "duration": "integer",
  "schedule_for": "string",
  "timezone": "string",
  "password": "string",
  "agenda": "string",
  "recurrence": {
    "type": "integer",
    "repeat_interval": "integer",
    "weekly_days": "string",
    "monthly_day": "integer",
    "monthly_week": "integer",
    "monthly_week_day": "integer",
    "end_times": "integer",
    "end_date_time": "string [date-time]"
  },
  "settings": {
    "host_video": "boolean",
    "participant_video": "boolean",
    "cn_meeting": "boolean",
    "in_meeting": "boolean",
    "join_before_host": "boolean",
    "mute_upon_entry": "boolean",
    "watermark": "boolean",
    "use_pmi": "boolean",
    "approval_type": "integer",
    "registration_type": "integer",
    "audio": "string",
    "auto_recording": "string",
    "enforce_login": "boolean",
    "enforce_login_domains": "string",
    "alternative_hosts": "string",
    "global_dial_in_countries": [
      "string"
    ],
    "registrants_email_notification": "boolean"
  }
}

"""

res_add_meeting = requests.post(API_ROOT + f"/v2/users/{userid}/meetings" , headers=headers)
added_meeting = res_add_meeting.json()
pprint(meetings)

