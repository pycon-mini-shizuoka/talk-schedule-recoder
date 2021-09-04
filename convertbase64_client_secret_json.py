import base64
from pathlib import Path
import sys

# クライアントシークレットのjsonファイルをbase64でエンコードする

fpath = Path(sys.argv[1]).absolute()

with fpath.open("rb") as client_secret_json_f:
    # print(client_secret_json_f)
    encoded_s = base64.b64encode(client_secret_json_f.read())

print(f"encoding:\n---\n {encoded_s}\n---")
