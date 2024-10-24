import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
import pytz  # タイムゾーン処理用

# プロジェクトのルートディレクトリを取得
ROOT_DIR = Path(__file__).parent.parent.absolute()

# 日本のタイムゾーンを設定
JP_TZ = pytz.timezone('Asia/Tokyo')

def get_jst_time():
    """現在の日本時間を取得"""
    return datetime.now(JP_TZ)

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

class JSTFormatter(logging.Formatter):
    """日本時間でログを記録するフォーマッタ"""
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        return JP_TZ.localize(dt)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime('%Y-%m-%d %H:%M:%S %Z')

def setup_logger(
    log_dir='logs',
    app_name='quiz_app',
    log_level=logging.INFO,
    user_id=None
):
    """新しいロガーインスタンスを設定して返す"""
    # ユーザー固有のロガー名を生成
    logger_name = f'xlsx_data_app_{user_id}' if user_id else 'xlsx_data_app'
    
    # 既存のロガーがある場合はそれを返す
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger
        
    try:
        # ログディレクトリの設定
        log_dir = os.path.join(ROOT_DIR, log_dir)
        os.makedirs(log_dir, exist_ok=True)
        
        # 新しいログファイル名を生成（日本時間のタイムスタンプを使用）
        timestamp = get_jst_time().strftime('%Y%m%d_%H%M%S')
        filename_prefix = f"{app_name}_{user_id}" if user_id else app_name
        log_filename = os.path.join(
            log_dir, 
            f"{filename_prefix}_{timestamp}.log"
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
        
        # フォーマッタの設定（日本時間対応）
        formatter = JSTFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S JST'
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

# デフォルトのグローバルロガーインスタンス
logger = setup_logger()

def get_user_logger(user_id):
    """ユーザー固有のロガーを取得"""
    return setup_logger(user_id=user_id)

# 外部からインポート可能な変数・関数
__all__ = ['logger', 'setup_logger', 'get_log_files', 'get_user_logger']