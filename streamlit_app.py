import streamlit as st
import pandas as pd
from components.quiz import show_quiz_screen
from components.result import show_result_screen
from components.admin import show_admin_screen
from utils.logger import setup_logger

# セッション状態の初期化
def init_session_state():
    if 'screen' not in st.session_state:
        st.session_state.screen = 'login'  # デフォルト画面をloginに変更
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
    if 'correct_count' not in st.session_state:
        st.session_state.correct_count = 0
    if 'total_attempted' not in st.session_state:
        st.session_state.total_attempted = 0
    if 'nickname' not in st.session_state:
        st.session_state.nickname = None
    if 'logger' not in st.session_state:
        st.session_state.logger = None

# ユーザーごとのロガーを取得
def get_user_logger():
    if st.session_state.logger is None and st.session_state.nickname:
        st.session_state.logger = setup_logger(user_id=st.session_state.nickname)
    return st.session_state.logger or setup_logger()

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('kaigai_latest.xlsx', sheet_name='sheet1', index_col=0)
        get_user_logger().info(f"データ読み込み成功: {len(df)}問の問題を読み込みました")
        return df
    except Exception as e:
        get_user_logger().error(f"データ読み込みエラー: {str(e)}")
        raise

def show_login_screen():
    st.title("ログイン")
    with st.form("login_form"):
        nickname = st.text_input("ニックネームを入力してください")
        submitted = st.form_submit_button("開始")
        
        if submitted and nickname:
            st.session_state.nickname = nickname
            st.session_state.screen = 'quiz'
            st.session_state.logger = setup_logger(user_id=nickname)
            get_user_logger().info(f"ユーザー[{nickname}]がログインしました")
            st.rerun()

def main():
    # セッション状態の初期化
    init_session_state()

    # ユーザーがログインしていない場合はログイン画面を表示
    if st.session_state.nickname is None:
        show_login_screen()
        return

    # サイドバーに管理者画面ボタンとログアウトボタンを追加
    with st.sidebar:
        if st.button("管理者画面"):
            st.session_state.screen = 'admin'
            get_user_logger().info(f"ユーザー[{st.session_state.nickname}]が管理者画面に移動しました")
            st.rerun()
        
        if st.button("ログアウト"):
            get_user_logger().info(f"ユーザー[{st.session_state.nickname}]がログアウトしました")
            st.session_state.nickname = None
            st.session_state.logger = None
            st.session_state.screen = 'login'
            st.rerun()

    # データの読み込み
    df = load_data()

    # 現在の画面に応じて表示を切り替え
    if st.session_state.screen == 'admin':
        show_admin_screen()
    else:
        show_quiz_screen(df)

if __name__ == "__main__":
    main()