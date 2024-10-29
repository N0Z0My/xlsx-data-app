import streamlit as st
from utils.logger import logger

def show_result_screen(df):
    st.title("🎉 クイズ完了！")
    
    accuracy = (st.session_state.correct_count / 20 ) * 100
    logger.info(f"クイズ完了 - 正解数: {st.session_state.correct_count}/ 20 , 正答率: {accuracy:.1f}%")
    
    # スコア表示
    st.markdown(f"## 最終スコア")
    st.markdown(f"### {st.session_state.correct_count} / 20 問 正解！")
    st.markdown(f"### 正答率: {accuracy:.1f}%")
    
    # 成績に応じたメッセージ
    if accuracy == 100:
        st.markdown("🌟 完璧です！素晴らしい成績です！")
    elif accuracy >= 80:
        st.markdown("🎈 素晴らしい成績です！")
    elif accuracy >= 60:
        st.markdown("👍 よく頑張りました！")
    else:
        st.markdown("💪 次は更に良い成績を目指しましょう！")
    
    # リトライボタン
    if st.button("もう一度チャレンジ"):
        reset_session_state()
        st.rerun()

def reset_session_state():
    logger.info("クイズを再スタート")
    st.session_state.screen = 'quiz'
    st.session_state.question_index = 0
    st.session_state.correct_count = 0
    st.session_state.total_attempted = 0
    st.session_state.answered_questions = set()