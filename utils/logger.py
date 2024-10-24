import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(
    log_dir='logs',
    app_name='xlsx-data-app',
    df_name='海外安全虎の巻',  
    log_level=logging.INFO,
    max_bytes=5*1024*1024,  # 5MB
    backup_count=5
):
    """
    より堅牢なロギング設定を行う関数
    
    Parameters:
    -----------
    log_dir : str
        ログファイルを保存するディレクトリパス
    app_name : str
        アプリケーション名（ログファイル名の一部として使用）
    df_name : str
        データフレームの名前（ログファイル名の一部として使用）
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
    
    try:
        # ログディレクトリの作成（存在しない場合）
        os.makedirs(log_dir, exist_ok=True)
        
        # タイムスタンプの生成（日付と時間を含む）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # ログファイル名の生成（データフレーム名、日付、時間を含む）
        log_filename = os.path.join(
            log_dir, 
            f"{app_name}_{df_name}_{timestamp}.log"
        )
        
        # ロガーの取得
        logger = logging.getLogger(f"{app_name}_{df_name}")
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
        
        # ログファイルが正常に作成されたことを確認
        if not os.path.exists(log_filename):
            raise FileNotFoundError(f"ログファイルの作成に失敗しました: {log_filename}")
        
        # 初期ログメッセージ
        logger.info(f"ログファイルを作成しました: {log_filename}")
        
        return logger
        
    except Exception as e:
        # エラーメッセージを標準エラー出力に出力
        print(f"ログ設定中にエラーが発生しました: {str(e)}", file=sys.stderr)
        raise
        
# 使用例
def example_usage():
    try:
        # データフレーム名を指定してロガーを設定
        logger = setup_logger(
            app_name='analysis_app',
            df_name='sales_data'
        )
        
        # ログの出力例
        logger.info("データ分析を開始します")
        logger.debug("データフレームの行数: 1000")
        logger.warning("欠損値が検出されました")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")