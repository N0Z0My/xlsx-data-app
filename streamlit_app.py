import streamlit as st
import pandas as pd
from openai import OpenAI
import asyncio
import logging
from datetime import datetime
import os
import components

# ログの設定
def setup_logger():
    # ログ保存用のディレクトリ作成
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # ログファイル名に日付を含める
    log_filename = f"logs/quiz_app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # ログの基本設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # コンソールにも出力
        ]
    )
    return logging.getLogger(__name__)

# ロガーの初期化
logger = setup_logger()

# OpenAIの設定
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# セッション状態の初期化
if 'screen' not in st.session_state:
    st.session_state.screen = 'quiz'
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'correct_count' not in st.session_state:
    st.session_state.correct_count = 0
if 'total_attempted' not in st.session_state:
    st.session_state.total_attempted = 0
if 'answered_questions' not in st.session_state:
    st.session_state.answered_questions = set()

async def evaluate_answer_with_gpt(question, options, user_answer):
    prompt = f"""
    問題: {question}
    選択肢: {options}
    ユーザーの回答: {user_answer}

    以下の手順でユーザーの回答を評価し、必ず指定された形式で回答してください：
    1. 問題文と選択肢から最も適切な選択肢を１つ選んでください。
    2. ユーザーの回答が最も適切な選択肢と一致するか評価してください。
    3. 以下の形式で厳密に回答してください：

    RESULT:[CORRECT] または RESULT:[INCORRECT]
    
    あなたの回答: {user_answer}
    
    正解: [適切な選択肢]
    
    解説: [正解の短い解説]
    """

    try:
        logger.info(f"GPT評価開始 - 問題: {question}, ユーザー回答: {user_answer}")
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4",
            temperature=0.4,
            messages=[
                {"role": "system", "content": "あなたは海外旅行の豊富な知識を持っていて、ユーザーの回答を評価する優秀な採点者です。必ず指定された形式で回答してください。"},
                {"role": "user", "content": prompt}
            ]
        )
        gpt_response = response.choices[0].message.content
        logger.info(f"GPT評価完了 - 結果: {gpt_response}")
        return gpt_response
    except Exception as e:
        error_msg = f"エラーが発生しました: {str(e)}"
        logger.error(error_msg)
        return error_msg

def show_result_screen():
    st.title("🎉 クイズ完了！")
    
    accuracy = (st.session_state.correct_count / len(df)) * 100
    logger.info(f"クイズ完了 - 正解数: {st.session_state.correct_count}/{len(df)}, 正答率: {accuracy:.1f}%")
    
    st.markdown(f"## 最終スコア")
    st.markdown(f"### {st.session_state.correct_count} / {len(df)} 問正解！")
    st.markdown(f"### 正答率: {accuracy:.1f}%")
    
    if accuracy == 100:
        st.markdown("🌟 完璧です！素晴らしい成績です！")
    elif accuracy >= 80:
        st.markdown("🎈 素晴らしい成績です！")
    elif accuracy >= 60:
        st.markdown("👍 よく頑張りました！")
    else:
        st.markdown("💪 次は更に良い成績を目指しましょう！")
    
    if st.button("もう一度チャレンジ"):
        logger.info("クイズを再スタート")
        st.session_state.screen = 'quiz'
        st.session_state.question_index = 0
        st.session_state.correct_count = 0
        st.session_state.total_attempted = 0
        st.session_state.answered_questions = set()
        st.rerun()

def show_quiz_screen():
    st.title("💡Quiz")
    
    if 'answered_questions' not in st.session_state:
        st.session_state.answered_questions = set()
    
    st.progress(st.session_state.question_index / len(df))
    st.write(f"問題 {st.session_state.question_index + 1} / {len(df)}")
    
    current_question = st.session_state.question_index
    
    if current_question in st.session_state.answered_questions:
        st.session_state.question_index += 1
        if st.session_state.question_index >= len(df):
            st.session_state.screen = 'result'
        st.rerun()
        return
    
    s_selected = df.loc[current_question]
    question = s_selected.loc['質問']
    optionA = s_selected.loc['選択肢A']
    optionB = s_selected.loc['選択肢B']
    optionC = s_selected.loc['選択肢C']
    options = [optionA, optionB, optionC]

    logger.info(f"問題表示 - 問題番号: {current_question + 1}, 問題: {question}")

    st.markdown(f'## {question}')

    select_button = st.radio(
        label='回答を選択してください',
        options=options,
        index=None,
        horizontal=True
    )

    if st.button('回答を確定する'):
        if select_button is None:
            logger.warning("回答が選択されていません")
            st.warning('回答を選択してください。')
        else:
            with st.spinner('GPT-4が回答を評価しています...'):
                gpt_response = asyncio.run(evaluate_answer_with_gpt(question, options, select_button))
            
            is_correct = "RESULT:[CORRECT]" in gpt_response
            
            # 結果のアニメーション表示
            st.markdown("---")
            components.html(
                f"""
                <div id="quiz-result-root" data-correct="{str(is_correct).lower()}"></div>
                """,
                height=200
            )
            
            if is_correct and current_question not in st.session_state.answered_questions:
                st.session_state.correct_count += 1
                logger.info(f"正解 - 問題番号: {current_question + 1}, ユーザー回答: {select_button}")
            else:
                logger.info(f"不正解 - 問題番号: {current_question + 1}, ユーザー回答: {select_button}")
            
            # GPTの解説を表示
            display_response = gpt_response.replace("RESULT:[CORRECT]", "").replace("RESULT:[INCORRECT]", "").strip()
            st.write(display_response)
            
            st.session_state.answered_questions.add(current_question)
            st.session_state.total_attempted += 1

    # 最後の問題かどうかでボタンの表示を変更
    is_last_question = current_question == len(df) - 1
    
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

def show_admin_screen():
    st.title("管理者画面 📊")
    
    # タブを作成
    tab1, tab2 = st.tabs(["📝 ログ閲覧", "📊 統計情報"])

    with tab1:
        st.header("ログ閲覧")
        
        # ログファイル一覧を取得
        log_files = sorted([f for f in os.listdir('logs') if f.startswith('quiz_app_')], reverse=True)
        
        if not log_files:
            st.info("ログファイルが見つかりません")
            return
            
        selected_log = st.selectbox(
            "ログファイルを選択", 
            log_files,
            format_func=lambda x: x.replace('quiz_app_', '').replace('.log', '')
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("ログを表示"):
                try:
                    with open(f"logs/{selected_log}", 'r', encoding='utf-8') as f:
                        log_contents = f.read()
                    st.text_area("ログ内容", log_contents, height=500)
                except Exception as e:
                    st.error(f"ログの読み込みに失敗しました: {str(e)}")
        
        with col2:
            if st.button("ログをダウンロード"):
                try:
                    with open(f"logs/{selected_log}", 'r', encoding='utf-8') as f:
                        log_contents = f.read()
                    st.download_button(
                        label="📥 ログファイルをダウンロード",
                        data=log_contents,
                        file_name=selected_log,
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"ログファイルの準備に失敗しました: {str(e)}")
    
    with tab2:
        st.header("統計情報")
        try:
            # ログファイルから統計情報を抽出
            with open(f"logs/{selected_log}", 'r', encoding='utf-8') as f:
                log_contents = f.readlines()
            
            # ログデータをパースしてDataFrameを作成
            log_data = []
            current_question = None
            current_answer = None
            current_result = None
            current_timestamp = None
            
            for line in log_contents:
                timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', line)
                if timestamp_match:
                    current_timestamp = timestamp_match.group(1)
                
                # 問題表示のログをパース
                question_match = re.search(r'問題表示 - 問題番号: (\d+), 問題: (.+)$', line)
                if question_match:
                    current_question = {
                        'timestamp': current_timestamp,
                        'question_number': question_match.group(1),
                        'question': question_match.group(2)
                    }
                
                # 回答結果のログをパース
                answer_match = re.search(r'(正解|不正解) - 問題番号: (\d+), ユーザー回答: (.+)$', line)
                if answer_match and current_question:
                    log_data.append({
                        'timestamp': current_timestamp,
                        'question_number': answer_match.group(2),
                        'question': current_question['question'],
                        'user_answer': answer_match.group(3),
                        'result': answer_match.group(1)
                    })
            
            # DataFrameを作成
            if log_data:
                df_log = pd.DataFrame(log_data)
                
                # 基本統計の表示
                correct_answers = len(df_log[df_log['result'] == '正解'])
                total_attempts = len(df_log)
                accuracy = (correct_answers / total_attempts) * 100 if total_attempts > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="総回答数", value=total_attempts)
                with col2:
                    st.metric(label="正解数", value=correct_answers)
                with col3:
                    st.metric(label="正答率", value=f"{accuracy:.1f}%")
                
                # エラー発生回数
                errors = len([line for line in log_contents if "ERROR" in line])
                if errors > 0:
                    st.warning(f"エラー発生回数: {errors}回")
                
                # データプレビュー
                st.subheader("データプレビュー")
                st.dataframe(df_log.head())
                
                # CSVダウンロードボタン
                csv = df_log.to_csv(index=False)
                st.download_button(
                    label="📥 CSVファイルをダウンロード",
                    data=csv,
                    file_name=f"quiz_statistics_{selected_log.replace('quiz_app_', '').replace('.log', '')}.csv",
                    mime="text/csv"
                )
                
                # 詳細な分析
                st.subheader("詳細分析")
                
                # 時間帯別の正答率
                df_log['hour'] = pd.to_datetime(df_log['timestamp']).dt.hour
                hourly_stats = df_log.groupby('hour')['result'].agg({
                    '回答数': 'count',
                    '正解数': lambda x: (x == '正解').sum()
                }).reset_index()
                hourly_stats['正答率'] = (hourly_stats['正解数'] / hourly_stats['回答数'] * 100).round(1)
                
                st.write("時間帯別の統計")
                st.dataframe(hourly_stats)
                
                # 問題別の正答率
                question_stats = df_log.groupby('question_number')['result'].agg({
                    '回答数': 'count',
                    '正解数': lambda x: (x == '正解').sum()
                })