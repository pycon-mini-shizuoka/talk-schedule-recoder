# 認証のテスト
import json
import os
from pprint import pprint

import dotenv
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
from pathlib import Path
import base64

# TODO:2021-09-05 base64でエンコードしたclient_secret.jsonをロードする
dotenv.load_dotenv()
client_secret_file = os.environ[""]

SCOPES = ['https://www.googleapis.com/auth/youtube']
flow = InstalledAppFlow.from_client_secrets_file(
    Path(__file__).parent / 'client_secret.json',
    scopes=SCOPES)

credentials = flow.run_console()

youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

try:
    list_streams_request = youtube.liveStreams().list(
        part='id,snippet',
        mine=True,
        maxResults=50
    )

    while list_streams_request:
        list_streams_response = list_streams_request.execute()

        for stream in list_streams_response.get('items', []):
            print('%s (%s)' % (stream['snippet']['title'], stream['id']))

        list_streams_request = youtube.liveStreams().list_next(
            list_streams_request, list_streams_response)

except HttpError:
    import traceback
    traceback.print_exc()