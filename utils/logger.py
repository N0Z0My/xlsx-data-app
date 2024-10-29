import os
from google.oauth2 import service_account
import google_auth_httplib2
import httplib2
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest
from googleapiclient.errors import HttpError
import logging
import json
from datetime import datetime
import pytz
import streamlit as st

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SHEET_ID = "1bvpz1W6hwzTLLPuK9X8C7QjivnDe1g_Di-Hmln9-xwM"
SHEET_NAME = "sheet1"

# 日本のタイムゾーンを設定
JP_TZ = pytz.timezone('Asia/Tokyo')
SCOPE = "https://www.googleapis.com/auth/spreadsheets"

class GoogleSheetsHandler(logging.Handler):
    """Google Sheetsにログを保存するハンドラ"""
    
    def __init__(self, spreadsheet_id, sheet_name='logs'):
        super().__init__()
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.gsheet_connector = self._connect_to_gsheet()
        self._setup_sheet()
    
    def _connect_to_gsheet(self):
        """Streamlitのシークレットを使用してGoogle Sheetsに接続"""
        try:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["connections"]["gcs"],
                scopes=[SCOPE]
            )
            
            def build_request(http, *args, **kwargs):
                new_http = google_auth_httplib2.AuthorizedHttp(
                    credentials, http=httplib2.Http()
                )
                return HttpRequest(new_http, *args, **kwargs)
                
            authorized_http = google_auth_httplib2.AuthorizedHttp(
                credentials, http=httplib2.Http()
            )
            
            service = build(
                "sheets",
                "v4",
                requestBuilder=build_request,
                http=authorized_http
            )
            return service.spreadsheets()
        except Exception as e:
            print(f"Google Sheets接続エラー: {str(e)}")
            raise

    def _setup_sheet(self):
        """シートのヘッダーを設定"""
        headers = [
            'created_at',
            'user_id',
            'level',
            'logger_name',
            'message',
            'extra_data'
        ]
        
        try:
            self.gsheet_connector.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A1:F1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
        except HttpError as e:
            print(f"シートの初期化中にエラーが発生: {e}")

    def emit(self, record):
        """ログレコードをGoogle Sheetsに書き込む"""
        try:
            # 追加情報の抽出
            extra_data = {
                key: value
                for key, value in record.__dict__.items()
                if key not in ['msg', 'args', 'exc_info', 'exc_text']
            }
            
            # ログデータの準備
            log_data = [
                datetime.now(JP_TZ).isoformat(),
                getattr(record, 'user_id', ''),
                record.levelname,
                record.name,
                self.format(record),
                json.dumps(extra_data, ensure_ascii=False)
            ]
            
            # スプレッドシートに追加
            self.gsheet_connector.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A:F',
                valueInputOption='USER_ENTERED',
                body={'values': [log_data]}
            ).execute()
            
        except Exception as e:
            print(f"Google Sheetsへのログ書き込み中にエラーが発生: {str(e)}")

def setup_logger(
    spreadsheet_id,
    log_level=logging.INFO,
    user_id=None
):
    """新しいロガーインスタンスを設定して返す"""
    logger_name = f'xlsx_data_app_{user_id}' if user_id else 'xlsx_data_app'
    
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger
    
    try:
        # Google Sheetsハンドラ
        sheets_handler = GoogleSheetsHandler(spreadsheet_id)
        sheets_handler.setLevel(log_level)
        
        # コンソールハンドラ
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # フォーマッタの設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S JST'
        )
        
        sheets_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # ハンドラを追加
        logger.addHandler(sheets_handler)
        logger.addHandler(console_handler)
        
        logger.setLevel(log_level)
        logger.info("新しいログセッションを開始しました")
        
        return logger
        
    except Exception as e:
        print(f"ログ設定中にエラーが発生しました: {str(e)}")
        raise

def get_logs(
    spreadsheet_id,
    user_id=None,
    level=None,
    limit=100
):
    """Google Sheetsからログを取得"""
    try:
        handler = GoogleSheetsHandler(spreadsheet_id)
        result = handler.gsheet_connector.values().get(
            spreadsheetId=spreadsheet_id,
            range=f'logs!A:F'
        ).execute()
        
        values = result.get('values', [])[1:]  # ヘッダーを除外
        
        # フィルタリング
        filtered_values = values
        if user_id:
            filtered_values = [row for row in filtered_values if row[1] == user_id]
        if level:
            filtered_values = [row for row in filtered_values if row[2] == level]
        
        return filtered_values[-limit:]
        
    except HttpError as e:
        print(f"ログの取得エラー: {e}")
        return []