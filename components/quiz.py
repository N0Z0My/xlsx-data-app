import streamlit as st
import streamlit.components.v1 as components
from utils.gpt import evaluate_answer_with_gpt
from utils.logger import setup_logger
import asyncio

# 問題数の制限を定数として定義
MAX_QUESTIONS = 20

def show_quiz_screen(df, logger=None):
    """クイズ画面を表示する
    
    Args:
        df: クイズデータを含むDataFrame
        logger: ログを記録するロガーオブジェクト
    """  
    
    if logger is None:
        logger = setup_logger(user_id=st.session_state.get('nickname'))
          
    st.title("💡Quiz")

    # セッション状態の初期化
    if 'answered_questions' not in st.session_state:
        st.session_state.answered_questions = set()
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = {}
    if 'answers_history' not in st.session_state:
        st.session_state.answers_history = {}
    
    current_progress = min(st.session_state.question_index, MAX_QUESTIONS)
    st.progress(current_progress / MAX_QUESTIONS)
    st.write(f"## 問題 {st.session_state.question_index + 1} / {MAX_QUESTIONS}")

    current_question = st.session_state.question_index
    
    # 20問完了時の処理
    if current_question >= MAX_QUESTIONS:
        logger.info(f"ユーザー[{st.session_state.nickname}] - {MAX_QUESTIONS}問完了")
        # 結果データの保存
        st.session_state.quiz_results = {
            'total_questions': MAX_QUESTIONS,
            'correct_count': sum(1 for v in st.session_state.correct_answers.values() if v),
            'answers_history': st.session_state.answers_history
        }
        st.session_state.screen = 'result'
        st.rerun()
        return
    
    # 既に回答済みの問題をスキップ
    if current_question in st.session_state.answered_questions:
        st.session_state.question_index += 1
        if st.session_state.total_attempted >= MAX_QUESTIONS:
            st.session_state.screen = 'result'
        st.rerun()
        return
    
    # 問題の表示
    s_selected = df.loc[current_question]
    question = s_selected.loc['質問']
    options = [s_selected.loc[f'選択肢{opt}'] for opt in ['A', 'B', 'C']]

    logger.info(f"ユーザー[{st.session_state.nickname}] - 問題表示 - 問題番号: {current_question + 1}, 問題: {question}")

    st.markdown(f'## {question}')

    select_button = st.radio('回答を選択してください', options, index=None, horizontal=True)

    if st.button('回答を確定する'):
        if select_button is None:
            st.warning('回答を選択してください。')
            return
        
        handle_answer(select_button, question, options, current_question, logger)

    show_navigation_buttons(current_question, logger)

def handle_answer(select_button, question, options, current_question, logger):
    with st.spinner('GPT-4が回答を評価しています...'):
        gpt_response = asyncio.run(evaluate_answer_with_gpt(question, options, select_button))
    
    is_correct = "RESULT:[CORRECT]" in gpt_response
    show_answer_animation(is_correct)
    
    # 回答結果の保存
    st.session_state.correct_answers[current_question] = is_correct
    st.session_state.answers_history[current_question] = {
        'question': question,
        'user_answer': select_button,
        'is_correct': is_correct,
        'explanation': gpt_response.replace("RESULT:[CORRECT]", "").replace("RESULT:[INCORRECT]", "").strip()
    }
    
    process_answer(is_correct, current_question, select_button, gpt_response, logger)  # loggerを追加

def show_answer_animation(is_correct):
    if is_correct:
        # 正解の場合のコンテナ
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.success("🎉 正解！")
                st.markdown("素晴らしい判断です！この知識は実際の旅行で役立つはずです。")
            
            with col2:
                st.markdown("""
                    <div style='background-color: #28a745; 
                              color: white; 
                              padding: 5px 10px; 
                              border-radius: 15px; 
                              text-align: center;'>
                        +1 point
                    </div>
                """, unsafe_allow_html=True)
    else:
        # 不正解の場合のコンテナ
        error_container = st.container()
        
        with error_container:
            st.error("💫 惜しい！")
            st.markdown("間違いから学ぶことで、より深い知識が身につきます。")
            
            # ワンポイントボックス
            st.markdown("""
                <div style='background-color: #f8f9fa; 
                          padding: 10px; 
                          border-radius: 5px; 
                          margin-top: 10px;'>
                    <strong style='color: #dc3545;'>ワンポイント:</strong><br>
                    解説をよく読んで、次の問題に活かしましょう！
                </div>
            """, unsafe_allow_html=True)

def show_navigation_buttons(current_question, logger):
    remaining_questions = MAX_QUESTIONS - st.session_state.total_attempted
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.session_state.total_attempted >= MAX_QUESTIONS:
            if st.button('結果を見る 🎉', use_container_width=True):
                logger.info(f"ユーザー[{st.session_state.nickname}] - {MAX_QUESTIONS}問完了 - 結果画面へ遷移")
                st.session_state.screen = 'result'
                st.rerun()
        else:
            if st.button('次の問題へ ➡️', use_container_width=True):
                logger.info(f"ユーザー[{st.session_state.nickname}] - 次の問題へ進む - 現在の問題番号: {current_question + 1}")
                st.session_state.question_index += 1
                st.rerun()

def process_answer(is_correct, current_question, select_button, gpt_response, logger):
    if is_correct and current_question not in st.session_state.answered_questions:
        st.session_state.correct_count += 1
        logger.info(f"ユーザー[{st.session_state.nickname}] - 正解 - 問題番号: {current_question + 1}, ユーザー回答: {select_button}")
    else:
        logger.info(f"ユーザー[{st.session_state.nickname}] - 不正解 - 問題番号: {current_question + 1}, ユーザー回答: {select_button}")
    
    display_response = gpt_response.replace("RESULT:[CORRECT]", "").replace("RESULT:[INCORRECT]", "").strip()
    st.write(display_response)
    
    st.session_state.answered_questions.add(current_question)
    st.session_state.total_attempted += 1