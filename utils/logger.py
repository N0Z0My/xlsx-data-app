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

# グローバル変数としてloggerを定義
logger = None

def setup_logger(
    spreadsheet_id=SPREADSHEET_ID,  # デフォルト値としてconfigから取得したIDを使用
    log_level=logging.INFO,
    user_id=None
):
    """新しいロガーインスタンスを設定して返す"""
    global logger
    
    # すでにloggerが設定されている場合は、それを返す
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

# 初期設定でロガーを作成
logger = setup_logger()