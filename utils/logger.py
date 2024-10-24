# utils/logger.py
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(
    log_dir='logs',
    app_name='xlsx_data_app',
    df_name='海外安全',
    log_level=logging.INFO,
    max_bytes=5*1024*1024,
    backup_count=30
):
    
    try:
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = os.path.join(
            log_dir, 
            f"{df_name}_{timestamp}.log"  # アプリ名を除外し、データフレーム名と時刻のみに
        )
        
        # グローバルなロガーを取得
        logger = logging.getLogger('xlsx_data_app')
        
        # ロガーが既に設定されている場合はそれを返す
        if logger.hasHandlers():
            return logger
            
        logger.setLevel(log_level)
        
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        if not os.path.exists(log_filename):
            raise FileNotFoundError(f"ログファイルの作成に失敗しました: {log_filename}")
        
        logger.info(f"ログファイルを作成しました: {log_filename}")
        
        return logger
        
    except Exception as e:
        print(f"ログ設定中にエラーが発生しました: {str(e)}", file=sys.stderr)
        raise

# デフォルトのロガーを作成
logger = setup_logger()

# このモジュールから直接インポート可能な変数として公開
__all__ = ['logger', 'setup_logger']