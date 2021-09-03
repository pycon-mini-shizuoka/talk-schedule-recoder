# ここで試したいこと
# スケジュール登録をまず試そう
# ストリーム設定は、YouTube Live側のAPIでストリームキーなど作れた時に

# requestsでやる

import os
import json
from typing import Tuple
import requests
from pathlib import Path

import dotenv
from pprint import pprint

dotenv.load_dotenv()
zoom_jwt_token = os.environ["ZOOM_JWT_TOKEN"]

API_ROOT = "https://api.zoom.us/v2"

headers = {
    'authorization': f"Bearer {zoom_jwt_token}",
    'content-type': "application/json"
    }

# クラウドレコーディング

# ストリームキー設定

meetingid = os.environ["TEST_RECODING_MEETINGID"]

# APIで操作

res_dl_recoding = requests.get(API_ROOT + f"/meetings/{meetingid}/recordings" ,
                    headers=headers)
print(res_dl_recoding)
dl_recoding = res_dl_recoding.json()

print("res config lviestream ")
pprint(dl_recoding)

# URLでDLしてファイル保存する

download_url = dl_recoding["recording_files"][0]["download_url"]
print(f"download url:{download_url}")
dl_video = requests.get(f"{download_url}?access_token={zoom_jwt_token}", stream=True)
print(dl_video)
with Path("dl_video.mp4").open("wb") as savefile:
  for chunk in dl_video.iter_content(chunk_size=1024):
      savefile.write(chunk)


## 気になるところ
"""
- ファイルが重くなった時にどうやって処理しようか悩みそう。
  - https://www.kite.com/python/answers/how-to-download-large-files-with-requests-in-python
  - requests.getのstream引数で有効にしておけばよさそう。そのあとチャンクサイズできりながら取得して保存かな
"""