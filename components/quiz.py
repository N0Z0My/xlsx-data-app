import streamlit as st
import streamlit.components.v1 as components  # この行を追加
from utils.logger import logger
from utils.gpt import evaluate_answer_with_gpt
import asyncio

def show_quiz_screen(df):
    st.title("##💡Quiz")
    
    if 'answered_questions' not in st.session_state:
        st.session_state.answered_questions = set()
    
    st.progress(st.session_state.question_index / len(df))
    st.write(f"##問題 {st.session_state.question_index + 1} / {len(df)}")
    
    current_question = st.session_state.question_index
    
    if current_question in st.session_state.answered_questions:
        st.session_state.question_index += 1
        if st.session_state.question_index >= len(df):
            st.session_state.screen = 'result'
        st.rerun()
        return
    
    s_selected = df.loc[current_question]
    question = s_selected.loc['質問']
    options = [s_selected.loc[f'選択肢{opt}'] for opt in ['A', 'B', 'C']]

    logger.info(f"問題表示 - 問題番号: {current_question + 1}, 問題: {question}")

    st.markdown(f'## {question}')

    select_button = st.radio('回答を選択してください', options, index=None, horizontal=True)

    if st.button('回答を確定する'):
        handle_answer(select_button, question, options, current_question)

    show_navigation_buttons(current_question, len(df))

def handle_answer(select_button, question, options, current_question):
    if select_button is None:
        logger.warning("回答が選択されていません")
        st.warning('回答を選択してください。')
        return

    with st.spinner('GPT-4が回答を評価しています...'):
        gpt_response = asyncio.run(evaluate_answer_with_gpt(question, options, select_button))
    
    is_correct = "RESULT:[CORRECT]" in gpt_response
    show_answer_animation(is_correct)
    process_answer(is_correct, current_question, select_button, gpt_response)

def show_answer_animation(is_correct):
    st.markdown("---")
    if is_correct:
        # 正解時の表示
        st.markdown("""
        <div style='padding: 20px; background-color: #E7F7E7; border-radius: 10px; border-left: 5px solid #28a745;'>
            <h2 style='color: #28a745; margin: 0; display: flex; align-items: center; gap: 10px;'>
                <span>🎉 正解！</span>
                <span style='font-size: 16px; background-color: #28a745; color: white; padding: 3px 10px; border-radius: 15px;'>
                    +1 point
                </span>
            </h2>
            <p style='color: #2E7D32; margin-top: 10px;'>
                素晴らしい判断です！この知識は実際の旅行で役立つはずです。
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 不正解時の表示
        st.markdown("""
        <div style='padding: 20px; background-color: #FEEDED; border-radius: 10px; border-left: 5px solid #dc3545;'>
            <h2 style='color: #dc3545; margin: 0;'>💫 惜しい！</h2>
            <p style='color: #712B2B; margin-top: 10px;'>
                間違いから学ぶことで、より深い知識が身につきます。
            </p>
            <div style='background-color: rgba(255,255,255,0.7); padding: 10px; border-radius: 5px; margin-top: 10px;'>
                <span style='font-weight: bold; color: #dc3545;'>ワンポイント:</span>
                <br>
                解説をよく読んで、次の問題に活かしましょう！
            </div>
        </div>
        """, unsafe_allow_html=True)

def process_answer(is_correct, current_question, select_button, gpt_response):
    if is_correct and current_question not in st.session_state.answered_questions:
        st.session_state.correct_count += 1
        logger.info(f"正解 - 問題番号: {current_question + 1}, ユーザー回答: {select_button}")
    else:
        logger.info(f"不正解 - 問題番号: {current_question + 1}, ユーザー回答: {select_button}")
    
    display_response = gpt_response.replace("RESULT:[CORRECT]", "").replace("RESULT:[INCORRECT]", "").strip()
    st.write(display_response)
    
    st.session_state.answered_questions.add(current_question)
    st.session_state.total_attempted += 1

def show_navigation_buttons(current_question, total_questions):
    is_last_question = current_question == total_questions - 1
    
    if is_last_question:
        if st.button('結果を見る 🎉'):
            logger.info("クイズ終了 - 結果画面へ遷移")
            st.session_state.screen = 'result'
            st.rerun()
    else:
        if st.button('次の問題へ ➡️'):
            logger.info(f"次の問題へ進む - 現在の問題番号: {current_question + 1}")
            st.session_state.question_index += 1
            st.rerun()