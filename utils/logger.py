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
from .config import SPREADSHEET_ID

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
]
JP_TZ = pytz.timezone('Asia/Tokyo')

# グローバル変数としてloggerを定義
logger = None

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
                scopes=SCOPE
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
        """シートの存在確認と初期設定"""
        try:
            # まずスプレッドシートの情報を取得
            spreadsheet = self.gsheet_connector.get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            # 既存のシート一覧を取得
            sheets = spreadsheet.get('sheets', [])
            sheet_names = [sheet['properties']['title'] for sheet in sheets]
            
            # 指定したシートが存在しない場合は新規作成
            if self.sheet_name not in sheet_names:
                request = {
                    'addSheet': {
                        'properties': {
                            'title': self.sheet_name
                        }
                    }
                }
                self.gsheet_connector.batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={'requests': [request]}
                ).execute()
            
            # ヘッダーを設定
            headers = [
                'created_at',
                'user_id',
                'level',
                'logger_name',
                'message',
                'extra_data'
            ]
            
            self.gsheet_connector.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A1:F1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
        except HttpError as e:
            print(f"シートの初期化中にエラーが発生: {e}")
            raise

    def add_row_to_gsheet(self, row_data):
        """
        Google Sheetsに1行のデータを追加
        
        Parameters:
        -----------
        row_data : list
            追加する行データのリスト
            
        Returns:
        --------
        bool
            追加が成功した場合はTrue、失敗した場合はFalse
        """
        try:
            self.gsheet_connector.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A:F',
                valueInputOption='USER_ENTERED',
                body={'values': [row_data]}
            ).execute()
            return True
        except Exception as e:
            print(f"行の追加中にエラーが発生: {str(e)}")
            return False

    def emit(self, record):
        """ログレコードをGoogle Sheetsに書き込む"""
        try:
            extra_data = {
                key: value
                for key, value in record.__dict__.items()
                if key not in ['msg', 'args', 'exc_info', 'exc_text']
            }
            
            log_data = [
                datetime.now(JP_TZ).isoformat(),
                getattr(record, 'user_id', ''),
                record.levelname,
                record.name,
                self.format(record),
                json.dumps(extra_data, ensure_ascii=False)
            ]
            
            self.add_row_to_gsheet(log_data)
            
        except Exception as e:
            print(f"Google Sheetsへのログ書き込み中にエラーが発生: {str(e)}")


def setup_logger(
    spreadsheet_id=SPREADSHEET_ID,
    log_level=logging.INFO,
    user_id=None
):
    """新しいロガーインスタンスを設定して返す"""
    global logger
    
    if logger is not None:
        return logger

    logger_name = f'xlsx_data_app_{user_id}' if user_id else 'xlsx_data_app'
    logger = logging.getLogger(logger_name)
    
    if logger.handlers:
        return logger
    
    try:
        sheets_handler = GoogleSheetsHandler(spreadsheet_id)
        sheets_handler.setLevel(log_level)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S JST'
        )
        
        sheets_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
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

# 初期設定でロガーを作成
logger = setup_logger()