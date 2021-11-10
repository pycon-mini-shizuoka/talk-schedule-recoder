# PyCon mini Shizuokaのトーク事前収録を行うZoom+YouTube Live設定の自動化スクリプト
# YouTube Liveのストリーム作成
# Zoomのレコーディングありスケジュール + YouTube Liveのストリーム設定
import datetime
import json
import os
import pickle
from pathlib import Path
from pprint import pprint
import sys

import dotenv
import requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 認証向けのトークンなどをロード
dotenv.load_dotenv()
zoom_jwt_token = os.environ["ZOOM_JWT_TOKEN"]

headers = {
    "authorization": f"Bearer {zoom_jwt_token}",
    "content-type": "application/json",
}

YT_STREAM_ID = os.environ["YT_STREAM_ID"]

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
CLIENT_SECRETS_FILE = Path(__file__).parent / "client_secret.json"


def generate_zoom_endpoint(endpoint_addr):
    return f"https://api.zoom.us/v2/{endpoint_addr}"


def get_google_authenticated_service():
    # ref: https://developers.google.com/sheets/api/quickstart/python#step_3_set_up_the_sample, https://dev.classmethod.jp/articles/oauth2client-is-deprecated/
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_console()
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)


def main(credentials):

    # TODO:2021-10-24 引数設定
    # 時間, フォーマットは"2021-11-01 21:00"
    # スピーカー名
    args = sys.argv
    # TODO:2021-10-25 ココ型チェックしたいな
    option_start_datetime = sys.argv[1]
    option_speaker_name = sys.argv[2]

    youtube = credentials
    # ref:https://github.com/youtube/api-samples/blob/master/python/create_broadcast.py

    # TODO:2021-10-24 ここは引数で登録
    options_broadcast_title = (
        f"PyCon Shizu 2021 事前収録レビュー: {option_speaker_name}さん {option_start_datetime}"
    )

    option_date = option_start_datetime.split(" ")[0]
    option_time = option_start_datetime.split(" ")[1]
    # TODO:2021-10-25 ここZoomとYT Liveの共有できるか試すこと
    options_start_time = f"{option_date}T{option_time}:00.0"
    options_privacy_status = "unlisted"

    print("load option:")
    print(f"start time: {options_start_time}")
    print(f"speaker_name: {option_speaker_name}")

    # タイムゾーン管理
    # 入力した時間は日本時間なので、UTCに変換する
    args_datetime_format = "%Y-%m-%d %H:%M"
    fix_timezone_youtube_datetime = (
        datetime.datetime.strptime(option_start_datetime, args_datetime_format)
        .astimezone()
        .isoformat()
    )

    try:
        # とりあえず決め打ちでの例
        insert_broadcast_response = (
            youtube.liveBroadcasts()
            .insert(
                part="snippet,status,contentDetails",
                body={
                    "contentDetails": {
                        "enableClosedCaptions": True,
                        "enableContentEncryption": True,
                        "enableDvr": True,
                        "enableEmbed": False,
                        "recordFromStart": True,
                        "enableAutoStart": True,
                        "enableAutoStop": True,
                        "startWithSlate": True,
                    },
                    "snippet": {
                        "title": options_broadcast_title,
                        "scheduledStartTime": fix_timezone_youtube_datetime,
                    },
                    "status": {
                        "selfDeclaredMadeForKids": False,
                        "privacyStatus": options_privacy_status,
                    },
                },
            )
            .execute()
        )

        b_snippet = insert_broadcast_response["snippet"]

        print(
            "Broadcast '%s' with title '%s' was published at '%s'."
            % (
                insert_broadcast_response["id"],
                b_snippet["title"],
                b_snippet["publishedAt"],
            )
        )
        # streamをbindする
        # ストリーミングの情報はすでにあるので、それを使う
        bind_broadcast_response = (
            youtube.liveBroadcasts()
            .bind(
                part="id,contentDetails",
                id=insert_broadcast_response["id"],
                streamId=YT_STREAM_ID,
            )
            .execute()
        )

        # pprint(bind_broadcast_response)

    except HttpError:
        import traceback

        traceback.print_exc()
        # TODO:2021-10-24 ここでエラーの場合は続行できないで終了
        print("error YouTube Liveの動画URLが生成できませんでした")
        exit()

    # TODO:2021-10-24 ここからzoomの処理

    # meetingの構造を作る
    # start_timeはisoのフォーマット。utcの時間にて。tzはTimezone表現
    create_meeting_json_template = """
    {
        "topic": "replace meeting title",
        "type": "2",
        "start_time": "replace time",
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
            "auto_recording": "local",
            "enforce_login": "false",
            "wating_room": "false"
        }
    }
    """

    # jsonをloadsしておく
    create_meeting_json = json.loads(create_meeting_json_template)
    create_meeting_json["topic"] = options_broadcast_title
    create_meeting_json["start_time"] = options_start_time

    # print("create meeting json:")
    # print(json.dumps(create_meeting_json))

    res_add_meeting = requests.post(
        generate_zoom_endpoint("users/me/meetings"),
        headers=headers,
        data=json.dumps(create_meeting_json),
    )

    added_meeting = res_add_meeting.json()

    # print("created meeting info")
    # pprint(added_meeting)

    # ライブストリーム設定

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
    config_livestream_json[
        "page_url"
    ] = f"https://youtu.be/{bind_broadcast_response['id']}"

    # print("config lviestream json:")
    # print(json.dumps(config_livestream_json))

    res_config_livestream = requests.patch(
        generate_zoom_endpoint(f"meetings/{meetingid}/livestream"),
        headers=headers,
        data=json.dumps(config_livestream_json),
    )
    # print(res_config_livestream)
    config_livestream = res_config_livestream.text

    # print("res config lviestream ")
    # pprint(config_livestream)

    print("----------\nresult:\n")
    print(f"------------\nYouTube Live Title: {options_broadcast_title}")
    print(f"Zoom URL:{added_meeting['join_url']}")
    print(f"YouTube Live URL:https://youtu.be/{bind_broadcast_response['id']}")
    print("----------\n")


if __name__ == "__main__":
    main(get_google_authenticated_service())
