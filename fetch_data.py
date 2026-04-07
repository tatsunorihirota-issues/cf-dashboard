#!/usr/bin/env python3
"""Google Sheets APIからCFデータを取得してJSONに保存"""
import json
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1udhfs0CzZmCH7i3uCk_2uVeeQB26dpfQIy1m-WHRyqo'
SHEET_GID = 679303218
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'f551580d4e0a5371', 'data.json')

def get_creds():
    """GitHub Actions環境変数またはローカルトークンファイルから認証"""
    token_json = os.environ.get('GOOGLE_TOKEN_JSON')
    if token_json:
        info = json.loads(token_json)
        creds = Credentials.from_authorized_user_info(info, SCOPES)
    else:
        token_path = os.path.expanduser('~/.config/gws/sheets_token.json')
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

def main():
    creds = get_creds()
    service = build('sheets', 'v4', credentials=creds)

    # シート一覧からターゲットシート名を取得
    meta = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        fields='sheets.properties'
    ).execute()

    target_title = None
    for sheet in meta['sheets']:
        if sheet['properties']['sheetId'] == SHEET_GID:
            target_title = sheet['properties']['title']
            break

    if not target_title:
        raise ValueError(f'Sheet with gid={SHEET_GID} not found')

    # データ取得
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{target_title}'!A1:AZ20"
    ).execute()

    rows = result.get('values', [])

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(rows, f, ensure_ascii=False)

    print(f'Saved {len(rows)} rows to {OUTPUT_PATH}')

if __name__ == '__main__':
    main()
