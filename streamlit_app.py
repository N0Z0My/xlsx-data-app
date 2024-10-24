import streamlit as st
import pandas as pd
from components.quiz import show_quiz_screen
from components.result import show_result_screen
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
    init_session_state()
    df = load_data()
    
    # メイン画面の表示
    if st.session_state.screen == 'quiz':
        show_quiz_screen(df)
    elif st.session_state.screen == 'result':
        show_result_screen(df)
    elif st.session_state.screen == 'admin':
        show_admin_screen()
    
    # サイドバーの管理者ボタン
    with st.sidebar:
        if st.button("👤 管理者画面"):
            st.session_state.screen = 'admin'
            st.rerun()

if __name__ == "__main__":
    main()