import streamlit as st
import streamlit.components.v1 as components
from utils.logger import get_user_logger
from utils.gpt import evaluate_answer_with_gpt
import asyncio

# 問題数の制限を定数として定義
MAX_QUESTIONS = 20

def show_quiz_screen(df):
    # ユーザーIDとしてニックネームを使用
    logger = get_user_logger(st.session_state.nickname)
    
    st.title("##💡Quiz")
    
    if 'answered_questions' not in st.session_state:
        st.session_state.answered_questions = set()
    
    current_progress = min(st.session_state.question_index, MAX_QUESTIONS)
    st.progress(current_progress / MAX_QUESTIONS)
    st.write(f"##問題 {st.session_state.question_index + 1} / {MAX_QUESTIONS}")
    
    if st.session_state.total_attempted >= MAX_QUESTIONS:
        logger.info(f"ユーザー[{st.session_state.nickname}] - {MAX_QUESTIONS}問完了")
        st.session_state.screen = 'result'
        st.rerun()
        return
    
    current_question = st.session_state.question_index
    
    if current_question in st.session_state.answered_questions:
        st.session_state.question_index += 1
        if st.session_state.total_attempted >= MAX_QUESTIONS:
            st.session_state.screen = 'result'
        st.rerun()
        return
    
    s_selected = df.loc[current_question]
    question = s_selected.loc['質問']
    options = [s_selected.loc[f'選択肢{opt}'] for opt in ['A', 'B', 'C']]

    logger.info(f"ユーザー[{st.session_state.nickname}] - 問題表示 - 問題番号: {current_question + 1}, 問題: {question}")

    st.markdown(f'## {question}')

    select_button = st.radio('回答を選択してください', options, index=None, horizontal=True)

    if st.button('回答を確定する'):
        handle_answer(select_button, question, options, current_question)

    show_navigation_buttons(current_question)

def handle_answer(select_button, question, options, current_question):
    logger = get_user_logger(st.session_state.nickname)
    
    if select_button is None:
        logger.warning(f"ユーザー[{st.session_state.nickname}] - 回答が選択されていません")
        st.warning('回答を選択してください。')
        return

    with st.spinner('GPT-4が回答を評価しています...'):
        gpt_response = asyncio.run(evaluate_answer_with_gpt(question, options, select_button))
    
    is_correct = "RESULT:[CORRECT]" in gpt_response
    show_answer_animation(is_correct)
    process_answer(is_correct, current_question, select_button, gpt_response)

# show_answer_animation関数は変更なし

def process_answer(is_correct, current_question, select_button, gpt_response):
    logger = get_user_logger(st.session_state.nickname)
    
    if is_correct and current_question not in st.session_state.answered_questions:
        st.session_state.correct_count += 1
        logger.info(f"ユーザー[{st.session_state.nickname}] - 正解 - 問題番号: {current_question + 1}, ユーザー回答: {select_button}")
    else:
        logger.info(f"ユーザー[{st.session_state.nickname}] - 不正解 - 問題番号: {current_question + 1}, ユーザー回答: {select_button}")
    
    display_response = gpt_response.replace("RESULT:[CORRECT]", "").replace("RESULT:[INCORRECT]", "").strip()
    st.write(display_response)
    
    st.session_state.answered_questions.add(current_question)
    st.session_state.total_attempted += 1

def show_navigation_buttons(current_question):
    logger = get_user_logger(st.session_state.nickname)
    remaining_questions = MAX_QUESTIONS - st.session_state.total_attempted
    
    st.write(f"残り {remaining_questions} 問")
    
    if st.session_state.total_attempted >= MAX_QUESTIONS:
        if st.button('結果を見る 🎉'):
            logger.info(f"ユーザー[{st.session_state.nickname}] - {MAX_QUESTIONS}問完了 - 結果画面へ遷移")
            st.session_state.screen = 'result'
            st.rerun()
    else:
        if st.button('次の問題へ ➡️'):
            logger.info(f"ユーザー[{st.session_state.nickname}] - 次の問題へ進む - 現在の問題番号: {current_question + 1}")
            st.session_state.question_index += 1
            st.rerun()