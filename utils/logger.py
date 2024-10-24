import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# プロジェクトのルートディレクトリを取得
ROOT_DIR = Path(__file__).parent.parent.absolute()

def get_log_files():
    """
    ログディレクトリ内のログファイル一覧を取得する
    
    Returns:
    --------
    list: ログファイルのリスト（新しい順）
    """
    log_dir = os.path.join(ROOT_DIR, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        return []
    
    # ログファイルを日付の新しい順にソート
    return sorted(
        [f for f in os.listdir(log_dir) if f.endswith('.log')],
        reverse=True
    )

def setup_logger(
    log_dir='logs',
    app_name='quiz_app',
    df_name='default_df',
    log_level=logging.INFO
):
    """
    ロギング設定を行う関数
    
    Parameters:
    -----------
    log_dir : str
        ログファイルを保存するディレクトリ
    app_name : str
        アプリケーション名
    df_name : str
        データフレーム名
    log_level : int
        ロギングレベル
        
    Returns:
    --------
    logging.Logger: 設定済みのロガーインスタンス
    """
    try:
        # 絶対パスでログディレクトリを指定
        log_dir = os.path.join(ROOT_DIR, log_dir)
        os.makedirs(log_dir, exist_ok=True)
        
        # ログファイル名の生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = os.path.join(
            log_dir, 
            f"{app_name}_{timestamp}.log"
        )
        
        # ロガーの取得と設定
        logger = logging.getLogger('xlsx_data_app')
        logger.setLevel(log_level)
        
        # 既存のハンドラをクリア（重複を防ぐ）
        if logger.hasHandlers():
            logger.handlers.clear()
        
        # ファイルハンドラの設定
        file_handler = RotatingFileHandler(
            log_filename,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
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
        
        # ハンドラの追加
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        logger.info(f"ログファイルを作成しました: {log_filename}")
        
        return logger
        
    except Exception as e:
        print(f"ログ設定中にエラーが発生しました: {str(e)}")
        raise

# デフォルトのロガーを作成
logger = setup_logger()

# 外部からインポート可能な変数・関数
__all__ = ['logger', 'setup_logger', 'get_log_files']