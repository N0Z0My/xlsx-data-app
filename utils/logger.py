import logging
import os
import sqlite3
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
import pytz
import json

# プロジェクトのルートディレクトリを取得
ROOT_DIR = Path(__file__).parent.parent.absolute()

# 日本のタイムゾーンを設定
JP_TZ = pytz.timezone('Asia/Tokyo')

class SQLiteHandler(logging.Handler):
    """SQLiteにログを保存するハンドラ"""
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        """ログテーブルの作成"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP NOT NULL,
                    user_id TEXT,
                    level TEXT NOT NULL,
                    logger_name TEXT,
                    message TEXT NOT NULL,
                    extra_data TEXT
                )
            ''')
            # インデックスの作成
            conn.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON logs(created_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON logs(user_id)')

    def emit(self, record):
        """ログレコードをDBに書き込む"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 追加情報の抽出
                extra_data = {
                    key: value
                    for key, value in record.__dict__.items()
                    if key not in ['msg', 'args', 'exc_info', 'exc_text']
                }
                
                cursor.execute('''
                    INSERT INTO logs 
                    (created_at, user_id, level, logger_name, message, extra_data)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now(JP_TZ).isoformat(),
                    getattr(record, 'user_id', None),
                    record.levelname,
                    record.name,
                    self.format(record),
                    json.dumps(extra_data)
                ))
        except Exception as e:
            print(f"SQLiteへのログ書き込み中にエラーが発生: {str(e)}")

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

# SQLiteからログを取得するユーティリティ関数
def get_logs_from_db(
    db_path=None,
    user_id=None,
    level=None,
    start_date=None,
    end_date=None,
    limit=100
):
    """データベースからログを取得"""
    if db_path is None:
        db_path = os.path.join(ROOT_DIR, 'logs', 'app_logs.db')

    query = 'SELECT * FROM logs WHERE 1=1'
    params = []
    
    if user_id:
        query += ' AND user_id = ?'
        params.append(user_id)
    
    if level:
        query += ' AND level = ?'
        params.append(level)
    
    if start_date:
        query += ' AND created_at >= ?'
        params.append(start_date.isoformat())
    
    if end_date:
        query += ' AND created_at <= ?'
        params.append(end_date.isoformat())
    
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        return cursor.execute(query, params).fetchall()

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
    logger_name = f'xlsx_data_app_{user_id}' if user_id else 'xlsx_data_app'
    
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger
        
    try:
        # ログディレクトリの設定
        log_dir = os.path.join(ROOT_DIR, log_dir)
        os.makedirs(log_dir, exist_ok=True)
        
        # SQLiteのデータベースパス
        db_path = os.path.join(log_dir, 'app_logs.db')
        
        # タイムスタンプの生成
        timestamp = get_jst_time().strftime('%Y%m%d_%H%M%S')
        filename_prefix = f"{app_name}_{user_id}" if user_id else app_name
        log_filename = os.path.join(
            log_dir, 
            f"{filename_prefix}_{timestamp}.log"
        )
        
        logger.setLevel(log_level)
        
        # 通常のファイルハンドラ
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=5*1024*1024,
            backupCount=15,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        
        # SQLiteハンドラ
        sqlite_handler = SQLiteHandler(db_path)
        sqlite_handler.setLevel(log_level)
        
        # コンソールハンドラ
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # フォーマッタの設定
        formatter = JSTFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S JST'
        )
        
        file_handler.setFormatter(formatter)
        sqlite_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # すべてのハンドラを追加
        logger.addHandler(file_handler)
        logger.addHandler(sqlite_handler)
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

# SQLiteからログを検索する便利な関数
def search_logs(keyword, user_id=None, limit=100):
    """ログの検索"""
    db_path = os.path.join(ROOT_DIR, 'logs', 'app_logs.db')
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM logs 
            WHERE message LIKE ? 
        '''
        params = [f'%{keyword}%']
        
        if user_id:
            query += ' AND user_id = ?'
            params.append(user_id)
            
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        return cursor.execute(query, params).fetchall()

# 外部からインポート可能な変数・関数
__all__ = [
    'logger', 
    'setup_logger', 
    'get_log_files', 
    'get_user_logger',
    'get_logs_from_db',
    'search_logs'
]