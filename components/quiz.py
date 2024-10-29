import streamlit as st
import streamlit.components.v1 as components
from utils.gpt import evaluate_answer_with_gpt
from utils.logger import setup_logger
import asyncio

# 問題数の制限を定数として定義
MAX_QUESTIONS = 20

def show_quiz_screen(df, logger=None):
    """クイズ画面を表示する関数"""
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
    if 'total_attempted' not in st.session_state:
        st.session_state.total_attempted = 0
    
    # 終了条件のチェック（total_attemptedベース）
    if st.session_state.total_attempted >= MAX_QUESTIONS:
        logger.info(f"ユーザー[{st.session_state.nickname}] - {MAX_QUESTIONS}問完了")
        st.session_state.quiz_results = {
            'total_questions': MAX_QUESTIONS,
            'correct_count': sum(1 for v in st.session_state.correct_answers.values() if v),
            'answers_history': st.session_state.answers_history
        }
        st.session_state.screen = 'result'
        st.rerun()
        return

    current_progress = st.session_state.total_attempted
    st.progress(current_progress / MAX_QUESTIONS)
    st.write(f"## 問題 {current_progress + 1} / {MAX_QUESTIONS}")
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

def process_answer(is_correct, current_question, select_button, gpt_response, logger):
    """回答を処理する関数"""
    # まず回答の正誤を処理
    if current_question not in st.session_state.answered_questions:
        if is_correct:
            logger.info(f"ユーザー[{st.session_state.nickname}] - 正解 - 問題番号: {st.session_state.total_attempted + 1}, ユーザー回答: {select_button}")
        else:
            logger.info(f"ユーザー[{st.session_state.nickname}] - 不正解 - 問題番号: {st.session_state.total_attempted + 1}, ユーザー回答: {select_button}")
        
        # 回答済みとしてマークする前にカウントを増やす
        st.session_state.total_attempted += 1
        st.session_state.answered_questions.add(current_question)
    
    # 解説を表示
    display_response = gpt_response.replace("RESULT:[CORRECT]", "").replace("RESULT:[INCORRECT]", "").strip()
    st.write(display_response)

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
    """紙吹雪エフェクト付きの改善された回答アニメーション表示"""
    if is_correct:
        st.markdown("""
            <style>
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(-10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes bounce {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-10px); }
                }
                @keyframes confetti {
                    0% { transform: translateY(0) rotate(0deg); opacity: 1; }
                    100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
                }
                .result-container {
                    animation: fadeIn 0.5s ease-out;
                }
                .bounce-icon {
                    display: inline-block;
                    animation: bounce 2s infinite;
                }
                .confetti {
                    position: absolute;
                    width: 10px;
                    height: 10px;
                    opacity: 0;
                }
                .confetti-piece {
                    position: absolute;
                    width: 8px;
                    height: 8px;
                    animation: confetti 3s ease-in-out infinite;
                }
            </style>
            <div class='result-container' style='
                background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                border: 2px solid #28a745;
                color: #155724;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                font-size: 24px;
                margin: 20px 0;
                position: relative;
                box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
                overflow: hidden;
            '>
                <div style='
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 4px;
                    background: linear-gradient(90deg, #28a745, #98e9ab);
                '></div>
                
                <!-- 紙吹雪エフェクト -->
                <script>
                    function createConfetti() {
                        const container = document.querySelector('.result-container');
                        const colors = ['#FFD700', '#FF6B6B', '#4CAF50', '#64B5F6', '#BA68C8'];
                        
                        for (let i = 0; i < 50; i++) {
                            const confetti = document.createElement('div');
                            confetti.className = 'confetti-piece';
                            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                            confetti.style.left = Math.random() * 100 + '%';
                            confetti.style.animationDelay = Math.random() * 2 + 's';
                            confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
                            container.appendChild(confetti);
                        }
                    }
                    createConfetti();
                </script>

                <span class='bounce-icon' style='font-size: 36px;'>🎉</span>
                <span style='margin-left: 10px; font-weight: bold;'>正解！</span>
                <div style='
                    background-color: #28a745;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    font-size: 18px;
                    font-weight: bold;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    display: flex;
                    align-items: center;
                    gap: 5px;
                '>
                    <span style='font-size: 20px;'>⭐</span>
                    +1 point
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(-10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
                .result-container {
                    animation: fadeIn 0.5s ease-out;
                }
                .pulse-icon {
                    display: inline-block;
                    animation: pulse 2s infinite;
                }
            </style>
            <div class='result-container' style='
                background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
                border: 2px solid #dc3545;
                color: #721c24;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                font-size: 30px;
                margin: 20px 0;
                position: relative;
                box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
                overflow: hidden;
            '>
                <div style='
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 4px;
                    background: linear-gradient(90deg, #dc3545, #ff8d96);
                '></div>
                <span class='pulse-icon' style='font-size: 36px;'>💫</span>
                <span style='margin-left: 10px; font-weight: bold;'>惜しい！</span>
                <div style='
                    font-size: 18px;
                    margin-top: 10px;
                    opacity: 0.8;
                '>
                    次の問題も頑張りましょう！
                </div>
            </div>
        """, unsafe_allow_html=True)

def show_navigation_buttons(current_question, logger):
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.session_state.total_attempted >= MAX_QUESTIONS:
            if st.button('結果を見る📚', use_container_width=True):
                logger.info(f"ユーザー[{st.session_state.nickname}] - {MAX_QUESTIONS}問完了 - 結果画面へ遷移")
                st.session_state.screen = 'result'
                st.rerun()
        elif current_question in st.session_state.answered_questions:
            if st.button('次の問題へ ➡️', use_container_width=True):
                logger.info(f"ユーザー[{st.session_state.nickname}] - 次の問題へ進む - 現在の問題番号: {st.session_state.total_attempted + 1}")
                next_question = current_question
                while next_question in st.session_state.answered_questions:
                    next_question = (next_question + 1) % len(df)
                st.session_state.question_index = next_question
                st.rerun()