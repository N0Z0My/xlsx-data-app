import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# プロジェクトのルートディレクトリを取得
ROOT_DIR = Path(__file__).parent.parent.absolute()

def get_log_files():
    """ログファイル一覧を取得"""
    log_dir = os.path.join(ROOT_DIR, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        return []
    
    return sorted(
        [f for f in os.listdir(log_dir) if f.endswith('.log')],
        reverse=True
    )

def setup_logger(
    log_dir='logs',
    app_name='quiz_app',
    log_level=logging.INFO
):
    """新しいロガーインスタンスを設定して返す"""
    # 既存のロガーがある場合はそれを返す
    logger = logging.getLogger('xlsx_data_app')
    if logger.handlers:
        return logger
        
    try:
        # ログディレクトリの設定
        log_dir = os.path.join(ROOT_DIR, log_dir)
        os.makedirs(log_dir, exist_ok=True)
        
        # 新しいログファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = os.path.join(
            log_dir, 
            f"{app_name}_{timestamp}.log"
        )
        
        logger.setLevel(log_level)
        
        # ファイルハンドラの設定
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=5*1024*1024,
            backupCount=15,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        
        # コンソールハンドラの設定
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # フォーマッタの設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # ハンドラを追加
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        logger.info(f"新しいログセッションを開始しました: {log_filename}")
        
        return logger
        
    except Exception as e:
        print(f"ログ設定中にエラーが発生しました: {str(e)}")
        raise

# グローバルなロガーインスタンス
logger = setup_logger()

# 外部からインポート可能な変数・関数
__all__ = ['logger', 'setup_logger', 'get_log_files']