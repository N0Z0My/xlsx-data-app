import streamlit as st
import pandas as pd
from components.quiz import show_quiz_screen
from components.result import show_result_screen
from components.admin import show_admin_screen
from utils.logger import setup_logger

def init_session_state():
    """セッション状態の初期化"""
    defaults = {
        'screen': 'login',
        'question_index': 0,
        'correct_count': 0,
        'total_attempted': 0,
        'nickname': None,
        'logger': None
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def init_logger():
    """ロガーの初期化と設定"""
    try:
        if st.session_state.logger is None:
            try:
                # gsheetセクションからspreadsheet.idを取得
                SPREADSHEET_ID = st.secrets.gsheet["spreadsheet_id"]
                user_id = st.session_state.nickname or "anonymous"
                st.session_state.logger = setup_logger(
                    spreadsheet_id=SPREADSHEET_ID,
                    user_id=user_id
                )
            except Exception as e:
                st.write("デバッグ - 利用可能なsecrets:", list(st.secrets.keys()))
                st.write("デバッグ - gsheetの内容:", dict(st.secrets.gsheet))
                st.error(f"spreadsheet IDの取得に失敗: {str(e)}")
                return False
        return True
    except Exception as e:
        st.error(f"ロガーの初期化に失敗しました: {str(e)}")
        return False
    
def log_action(message, level="info"):
    """安全なロギング関数"""
    if hasattr(st.session_state, 'logger') and st.session_state.logger is not None:
        logger_func = getattr(st.session_state.logger, level, None)
        if logger_func:
            try:
                logger_func(message)
            except Exception as e:
                st.warning(f"ログの記録に失敗しました: {str(e)}")

@st.cache_data
def load_data():
    """データの読み込み"""
    try:
        df = pd.read_excel('f_kaigai.xlsx', sheet_name='sheet1', index_col=0)
        log_action(f"データ読み込み成功: {len(df)}問の問題を読み込みました")
        return df
    except Exception as e:
        log_action(f"データ読み込みエラー: {str(e)}", level="error")
        st.error("データの読み込みに失敗しました。")
        return None

def show_sidebar():
    """サイドバーの表示"""
    with st.sidebar:
        if st.button("管理者画面"):
            st.session_state.screen = 'admin'
            log_action(f"ユーザー[{st.session_state.nickname}]が管理者画面に移動しました")
            st.rerun()
        
        if st.session_state.nickname:
            if st.button("ログアウト"):
                log_action(f"ユーザー[{st.session_state.nickname}]がログアウトしました")
                # セッション状態のリセット
                st.session_state.nickname = None
                st.session_state.logger = None
                st.session_state.screen = 'login'
                st.rerun()

def show_login_screen():
    """ログイン画面の表示"""
    st.title("ログイン")
    with st.form("login_form"):
        nickname = st.text_input("ニックネームを入力してください")
        submitted = st.form_submit_button("開始")
        
        if submitted and nickname:
            st.session_state.nickname = nickname
            st.session_state.screen = 'quiz'
            
            # ロガーの再初期化
            if init_logger():
                log_action(f"ユーザー[{nickname}]がログインしました")
                st.rerun()
            else:
                st.error("ログインできません。システム管理者に連絡してください。")

def main():
    # 初期化処理
    init_session_state()
    init_logger()

    # サイドバーの表示
    show_sidebar()

    # 画面の表示を切り替え
    if st.session_state.screen == 'admin':
        show_admin_screen()
    elif st.session_state.nickname is None:
        show_login_screen()
    else:
        # データの読み込み
        df = load_data()
        if df is not None:
            show_quiz_screen(df)
        else:
            st.error("問題データを読み込めませんでした。")

if __name__ == "__main__":
    main()