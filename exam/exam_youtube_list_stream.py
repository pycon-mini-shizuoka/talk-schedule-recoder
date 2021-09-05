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
import requests
from pathlib import Path
import base64

# TODO:2021-09-05 base64でエンコードしたclient_secret.jsonをロードする
dotenv.load_dotenv()
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
    # ref:https://github.com/youtube/api-samples/blob/master/python/list_streams.py
    try:
        list_streams_request = youtube.liveStreams().list(
            part='id,snippet',
            mine=True,
            maxResults=50
        )
        # ページネーション的な処理っぽい。一度に得られる結果は限られるので
        while list_streams_request:
            list_streams_response = list_streams_request.execute()

            for stream in list_streams_response.get('items', []):
                print('%s (%s)' % (stream['snippet']['title'], stream['id']))

            list_streams_request = youtube.liveStreams().list_next(
                list_streams_request, list_streams_response)

    except HttpError:
        import traceback
        traceback.print_exc()

if __name__ =="__main__":
    main(get_authenticated_service())