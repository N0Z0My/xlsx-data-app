import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(
    log_dir='logs',
    app_name='海外旅行',
    log_level=logging.INFO,
    max_bytes=5*1024*1024,  # 5MB
    backup_count=10
):
    """
    より堅牢なロギング設定を行う関数
    
    Parameters:
    -----------
    log_dir : str
        ログファイルを保存するディレクトリパス
    app_name : str
        アプリケーション名（ログファイル名の一部として使用）
    log_level : int
        ロギングレベル（logging.DEBUG, logging.INFO など）
    max_bytes : int
        ログファイルの最大サイズ（バイト）
    backup_count : int
        保持する過去ログファイルの数
    
    Returns:
    --------
    logging.Logger
        設定済みのロガーインスタンス
    """
    
    # ログディレクトリの作成（存在しない場合）
    os.makedirs(log_dir, exist_ok=True)
    
    # ログファイル名の生成
    log_filename = os.path.join(
        log_dir, 
        f"{app_name}_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    # ロガーの取得
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)
    
    # 既存のハンドラをクリア（重複を防ぐため）
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # ファイルハンドラの設定（ローテーション付き）
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    # コンソールハンドラの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # フォーマッタの作成と設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # ハンドラの追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 使用例
logger = setup_logger()