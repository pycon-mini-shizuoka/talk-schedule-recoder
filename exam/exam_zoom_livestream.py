# requestsでやる

import os
import json
import requests

import dotenv
from pprint import pprint

dotenv.load_dotenv()
zoom_jwt_token = os.environ["ZOOM_JWT_TOKEN"]

API_ROOT = "https://api.zoom.us/v2"

headers = {
    'authorization': f"Bearer {zoom_jwt_token}",
    'content-type': "application/json"
    }

# meetingの構造を作る
create_meeting_json_template = """
{
  "topic": "wip:apitest:ライブストリーム設定あり",
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

print("create meeting json:")
print(json.dumps(create_meeting_json))

res_add_meeting = requests.post(API_ROOT + f"/users/me/meetings" ,
                    headers=headers,
                    data=json.dumps(create_meeting_json))
# print(res_add_meeting)

added_meeting = res_add_meeting.json()

print("created meeting info")
pprint(added_meeting)

# ライブストリーム設定

# ストリームキー設定

meetingid = added_meeting["id"]
yt_stream_key = os.environ["YT_STREAM_KEY"]

# APIで操作

# このどれもマスト。page_urlは適当なアドレスでよさそう
stream_setting_json = """
{
  "stream_url": "rtmp://a.rtmp.youtube.com/live2",
  "stream_key": "yt_stream_key",
  "page_url": "https://shizuoka.pycon.jp"
}
"""

config_livestream_json = json.loads(stream_setting_json)

config_livestream_json["stream_key"] = yt_stream_key

print("config lviestream json:")
print(json.dumps(config_livestream_json))

res_config_livestream = requests.patch(API_ROOT + f"/meetings/{meetingid}/livestream" ,
                    headers=headers,
                    data=json.dumps(config_livestream_json))
print(res_config_livestream)
config_livestream = res_config_livestream.text

print("res config lviestream ")
pprint(config_livestream)


## 気になるところ
"""
- YouTubeのライブストリーム設定をしてみた
- Zoomのユーザー設定を変更する必要ある。 -> 設定済み
  - カスタムライブストリーム設定がひつようっぽい　
- youTube ライブの設定は普通に作成すればいい。開始時間とかは余裕をもって作るといいと思う（10分前とか）
- 自動スタート自動ストップを有効にしておけばよさそう。
- **Zoom側ではライブストリームの自動開始はできないっぽい。手動でやる必要があるっぽい**
  - 操作方法を共有しておけばよさそう。
- クラウドレコーディングとライブストリーム自体は両方とも実行可能だった
 ライブストリーム後にYouTube側の動画のDLもできるかチェック。

- 次はzoomのクラウドレコーディング結果をAPI経由でDLできるかチェックかな。

- zoomの設定で気になるところがあったのでやっておいた
  - クラウド記録>クラウド記録の詳細設定>サードパーティビデオエディター用に記録を最適化する にチェックを入れる。
  - 編集はある程度自動で行う予定だけど、（カットぐらいなので手動でもいいけど）編集ソフトで動かないと困るので、あらかじめ最適化設定をしておく。動画のサイズが増えるけどどの程度かはわからない
"""