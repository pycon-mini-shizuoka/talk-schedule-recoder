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
  "topic": "wip:apitest:日本語テストです もう一つ",
  "type": "2",
  "start_time": "2021-09-02T13:50:00Z",
  "duration": "45",
  "timezone": "Asia/Tokyo",
  "password": "2021091022",
  "agenda": "",
  "settings": {
    "host_video": "true",
    "participant_video": "true",
    "join_before_host": "true",
    "watermark": "false",
    "audio": "voip",
    "auto_recording": "cloud",
    "enforce_login": "false",
    "wating_room": "false"
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

## 気になるところ
"""
- API操作は特に問題なし
- ローカルレコードをしたときに、Zoomの参加者の顔が小さすぎる問題点
- 悩ましい所だけどあきらめてもらうしかないかも...
- 一応ほかのマシンでも試そう...
  -> 参加者として参加するとローカル録画が自動的に動かないことがわかる💦
  -> これだと開始タイミングでバックアップが取れないから、手動で録画してもらう必要がある（これはしょうがないかな）
  クラウドレコーディングだとどうなるか調べてみよう -> todoに入れる
- ミーティングひとつのみの話でもあるから、starturlを渡してしまっても良いかもしれない。ただその場合はユーザー名も全部ミーティング発行者のユーザーっぽい
  - 主催者アドレスを使って、自動的に起動してOBSのvirtualカメラで録画用ユーザーとして自動参加させるのもひとつ
    - 期間中 or ミーティングスケジュールにのっとって起動して、操作するRPAが必要。正直面倒
  - レコーディングはYouTube Live側で任せちゃうのもいいかな。
  - クラウドレコーディングだったら、参加者も録画できた。開始許諾はやる必要があるから連絡しよう。
  
"""