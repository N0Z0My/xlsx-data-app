import streamlit as st
import pandas as pd
from components.quiz import show_quiz_screen
#from components.result import show_result_screen
from components.admin import show_admin_screen
from utils.logger import logger

# セッション状態の初期化
def init_session_state():
    if 'screen' not in st.session_state:
        st.session_state.screen = 'quiz'
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
    if 'correct_count' not in st.session_state:
        st.session_state.correct_count = 0
    if 'total_attempted' not in st.session_state:
        st.session_state.total_attempted = 0

logger.info("Streamlitアプリケーションを開始します")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('kaigai_latest.xlsx', sheet_name='sheet1', index_col=0)
        logger.info(f"データ読み込み成功: {len(df)}問の問題を読み込みました")
        return df
    except Exception as e:
        logger.error(f"データ読み込みエラー: {str(e)}")
        raise

def main():
    # セッション開始時のみログを記録
    if 'session_initialized' not in st.session_state:
        logger.info("アプリケーションを開始します")
        st.session_state.session_initialized = True

    # 画面の状態管理
    if 'screen' not in st.session_state:
        st.session_state.screen = 'quiz'

    # 現在の画面に応じて表示を切り替え
    if st.session_state.screen == 'admin':
        show_admin_screen()
    else:
        show_quiz_screen()  # クイズ画面の表示関数


if __name__ == "__main__":
    main()