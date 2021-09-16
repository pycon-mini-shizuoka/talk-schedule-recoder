# ref: https://github.com/Azure-Samples/ms-identity-python-daemon/tree/master/1-Call-MsGraph-WithSecret

import sys  # For simplicity, we'll read config file from 1st CLI param sys.argv[1]
import json
import logging

import requests
import msal

base_endpoint = "https://graph.microsoft.com/v1.0/"

# Optional logging
# logging.basicConfig(level=logging.DEBUG)

config = json.load(open(sys.argv[1]))

user_id = config["user_id"]

# Create a preferably long-lived app instance which maintains a token cache.
app = msal.ConfidentialClientApplication(
    config["client_id"], authority=config["authority"],
    client_credential=config["secret"],
    # token_cache=...  # Default cache is in memory only.
                       # You can learn how to use SerializableTokenCache from
                       # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
    )

# The pattern to acquire a token looks like this.
result = None

# Firstly, looks up a token from cache
# Since we are looking for token for the current app, NOT for an end user,
# notice we give account parameter as None.
result = app.acquire_token_silent(config["scope"], account=None)

if not result:
    logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
    result = app.acquire_token_for_client(scopes=config["scope"])

if "access_token" in result:
    # Calling graph using the access token
    graph_data = requests.get(  # Use token to call downstream service
        base_endpoint + f"users/{user_id}/drive/",
        headers={'Authorization': 'Bearer ' + result['access_token']}, ).json()
    print("Graph API call result: ")
    print(json.dumps(graph_data, indent=2))
    
    import urllib.parse

    item_path = urllib.parse.quote("pycon-mini-shizuoka/talk-recoder/")
    graph_data = requests.get(  # Use token to call downstream service
        base_endpoint + f"users/{user_id}/drive/root:/{item_path}",
        headers={'Authorization': 'Bearer ' + result['access_token']}, ).json()
    print("Graph API call result: user_id + drivepath")
    print(json.dumps(graph_data, indent=2))

    folder_id = graph_data["id"]
    print(f"folder_id:{folder_id}")

    # ファイルのアップロード

    # 10MBのビデオを用意しよう
    
    filename = "test_video.mp4"

    # セッション作成
    file_url = urllib.parse.quote(filename)
    result = requests.post(
        f'{base_endpoint}users/{user_id}/tems/{folder_id}:/{file_url}:/createUploadSession',
        headers={'Authorization': 'Bearer ' + result['access_token']},
        json={
            '@microsoft.graph.conflictBehavior': 'replace',
            'description': 'A large test file',
            'fileSystemInfo': {'@odata.type': 'microsoft.graph.fileSystemInfo'},
            'name': filename
        }
    )
    upload_session = result.json()
    upload_url = upload_session['uploadUrl']

    import os

    st = os.stat(filename)
    size = st.st_size
    CHUNK_SIZE = 10485760
    chunks = int(size / CHUNK_SIZE) + 1 if size % CHUNK_SIZE > 0 else 0

    with open(filename, 'rb') as fd:
        start = 0
        for chunk_num in range(chunks):
            chunk = fd.read(CHUNK_SIZE)
            bytes_read = len(chunk)
            upload_range = f'bytes {start}-{start + bytes_read - 1}/{size}'
            print(f'chunk: {chunk_num} bytes read: {bytes_read} upload range: {upload_range}')
            result = requests.put(
                upload_url,
                headers={
                    'Content-Length': str(bytes_read),
                    'Content-Range': upload_range
                },
                data=chunk
            )
            result.raise_for_status()
            start += bytes_read

else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug

# メモ
"""
- ファイルのアップロードは、小さいサイズではなく大きなサイズを想定して、念のためにセッションをつくってアップする
- セッション作成をして一時的に保持、そのあと

- トラブってダウンロードができない場合、セッション維持方法をかんがえる必要がある
  - 状況をファイルにダンプしておいてもいいけど、redisとかに置いておくのもいいかな。
  - 考えるべきところは、ネットが切れる, サーバーが落ちるってところで、ネットが切れた場合はredisからセッション情報取ればいいって考え
  - といっても、その時はアップロードスクリプトが走っているから、リトライし続けて復帰すればいい。
  - （回数もあるし）復帰できないときはリトライ終了してセッションを保持して、ある程度タイミングを開けてから行えるようにする（これもcronかな）

"""