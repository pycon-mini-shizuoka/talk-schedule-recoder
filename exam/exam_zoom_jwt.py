# ref: https://marketplace.zoom.us/docs/guides/auth/jwt#sample-code
import os

import http.client
import dotenv

conn = http.client.HTTPSConnection("api.zoom.us")

dotenv.load_dotenv()
zoom_jwt_token = os.environ["ZOOM_JWT_TOKEN"]

headers = {
    'authorization': f"Bearer {zoom_jwt_token}",
    'content-type': "application/json"
    }

print(headers)

conn.request("GET", "/v2/users?status=active&page_size=30&page_number=1", headers=headers)

res = conn.getresponse()
data = res.read()

from pprint import pprint
pprint(data.decode("utf-8"))