# 認証のテスト
import json
import os
from pprint import pprint
import pickle

import dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import datetime
from pathlib import Path
import base64

# TODO:2021-09-05 base64でエンコードしたclient_secret.jsonをロードする
dotenv.load_dotenv()
YT_STREAM_ID = os.environ["YT_STREAM_ID"]

# client_secret_file = os.environ[""]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ['https://www.googleapis.com/auth/youtube']
CLIENT_SECRETS_FILE=Path(__file__).parent / 'client_secret.json'

def get_authenticated_service():
    # ref: https://developers.google.com/sheets/api/quickstart/python#step_3_set_up_the_sample, https://dev.classmethod.jp/articles/oauth2client-is-deprecated/
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_console()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)


def main(credentials):
    youtube = credentials
    # ref:https://github.com/youtube/api-samples/blob/master/python/create_broadcast.py
    options_broadcast_title = "pyconshizu api test " + datetime.datetime.now().strftime("%Y%m%d%H%M")
    options_start_time = "2021-09-08T00:00:00.0Z"
    options_broadcast_min = 40
    options_privacy_status = "unlisted"
    try:
        # とりあえず決め打ちでの例
        insert_broadcast_response = youtube.liveBroadcasts().insert(
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
                    "scheduledStartTime": options_start_time,
                },
                "status": {
                    "selfDeclaredMadeForKids": False,
                    "privacyStatus": options_privacy_status
                }
            }
        ).execute()

        b_snippet = insert_broadcast_response["snippet"]

        print("Broadcast '%s' with title '%s' was published at '%s'." % (
            insert_broadcast_response["id"], b_snippet["title"], b_snippet["publishedAt"]))

        # broadcastの設定をする

        # update_broadcast_request = youtube.liveBroadcasts().update(
        #     part="snippet,status,contentDetails",
        #     body={
        #         "id": insert_broadcast_response["id"],
        #         # "contentDetails": {
        #         #     "enableClosedCaptions": True,
        #         #     "enableContentEncryption": True,
        #         #     "enableDvr": True,
        #         #     "enableEmbed": False,
        #         #     "recordFromStart": True,
        #         #     "enableAutoStart": True,
        #         #     "enableAutoStop": True,
        #         #     "startWithSlate": True,
        #         # },
        #         "snippet": {
        #             "title": options_broadcast_title,
        #             "scheduledStartTime": options_start_time,
        #             # "scheduledEndTime": options_end_time
        #         },
        #         "status": {
        #             "privacyStatus": options_privacy_status
        #         }
        #     }
        # ).execute()

        # cb_snippet = update_broadcast_request["snippet"]

        # print("Broadcast '%s' with title '%s' was updated ." % (
        #     update_broadcast_request["id"], cb_snippet["title"])
        # )

        # streamをbindする
        # ストリーミングの情報はすでにあるので、それを使う
        bind_broadcast_response = youtube.liveBroadcasts().bind(
            part="id,contentDetails",
            id=insert_broadcast_response["id"],
            streamId=YT_STREAM_ID
        ).execute()

        print("Broadcast '%s' was bound to stream '%s'." % (
            bind_broadcast_response["id"],
            bind_broadcast_response["contentDetails"]["boundStreamId"]))

    except HttpError:
        import traceback
        traceback.print_exc()

if __name__ =="__main__":
    main(get_authenticated_service())


# 気になること

"""
- youtube livestreming apiの操作で（というかGoogleのAPIライブラリの使い方として
  partのオプションを指定するとき、送るbodyに入れたいデータの名称としては必ず入れないといけないのを注意すること

"""