# 認証のテスト
import json
import os
from pprint import pprint


# メモ

"""
- アクセス認証は Azure Portalから行う
- アプリの作成 > クライアントシークレット > アプリのアクセス許可 の順で進める
- OneDriveはGraph File APIから扱うらしい。アクセス許可は"アプリケーションのアクセス許可"から Files.ReadWrite.Allを選ぶ
- 保存先のディレクトリは作っておく（pycon_shizu_talk_recoderのような名称で）

"""