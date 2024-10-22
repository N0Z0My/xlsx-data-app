import streamlit as st
import pandas as pd
from openai import OpenAI
import asyncio

# OpenAIの設定
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# セッション状態の初期化
if 'screen' not in st.session_state:
    st.session_state.screen = 'quiz'  # 'quiz' または 'result'
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'correct_count' not in st.session_state:
    st.session_state.correct_count = 0
if 'total_attempted' not in st.session_state:
    st.session_state.total_attempted = 0

async def evaluate_answer_with_gpt(question, options, user_answer):
    # 既存のevaluate_answer_with_gpt関数をそのまま使用
    # ...（変更なし）

# データフレームの読み込み
@st.cache_data
def load_data():
    return pd.read_excel('kaigai_latest.xlsx', sheet_name='sheet1', index_col=0)

df = load_data()

# 結果画面の表示
def show_result_screen():
    st.title("🎉 クイズ完了！")
    
    # 結果の表示
    st.markdown(f"## 最終スコア")
    st.markdown(f"### {st.session_state.correct_count} / {len(df)} 問正解！")
    
    # 正答率の計算と表示
    accuracy = (st.session_state.correct_count / len(df)) * 100
    st.markdown(f"### 正答率: {accuracy:.1f}%")
    
    # コメントの表示
    if accuracy == 100:
        st.markdown("🌟 完璧です！素晴らしい成績です！")
    elif accuracy >= 80:
        st.markdown("🎈 素晴らしい成績です！")
    elif accuracy >= 60:
        st.markdown("👍 よく頑張りました！")
    else:
        st.markdown("💪 次は更に良い成績を目指しましょう！")
    
    # 最初からやり直すボタン
    if st.button("もう一度チャレンジ"):
        st.session_state.screen = 'quiz'
        st.session_state.question_index = 0
        st.session_state.correct_count = 0
        st.session_state.total_attempted = 0
        st.rerun()

# メイン画面の表示
def show_quiz_screen():
    st.title("💡Quiz")
    
    # 現在の進捗を表示
    st.progress(st.session_state.question_index / len(df))
    st.write(f"問題 {st.session_state.question_index + 1} / {len(df)}")
    
    # 現在の問題を取得
    current_question = st.session_state.question_index
    s_selected = df.loc[current_question]
    question = s_selected.loc['質問']
    optionA = s_selected.loc['選択肢A']
    optionB = s_selected.loc['選択肢B']
    optionC = s_selected.loc['選択肢C']
    options = [optionA, optionB, optionC]

    st.markdown(f'## {question}')

    select_button = st.radio(label='回答を選択してください',
                     options=options,
                     index=None,
                     horizontal=True)

    # 回答を確定するボタン
    if st.button('回答を確定する'):
        if select_button is None:
            st.warning('回答を選択してください。')
        else:
            with st.spinner('GPT-4が回答を評価しています...'):
                gpt_response = asyncio.run(evaluate_answer_with_gpt(question, options, select_button))
            st.write(gpt_response)
            
            # 正解かどうかを判定して正解数をカウント
            if "正解" in gpt_response:
                st.session_state.correct_count += 1
            st.session_state.total_attempted += 1

    # 次の問題に進むボタン
    if st.button('次の問題へ'):
        st.session_state.question_index += 1
        if st.session_state.question_index >= len(df):
            st.session_state.screen = 'result'  # 全問題が終わったら結果画面へ
        st.rerun()

# メイン処理
if st.session_state.screen == 'quiz':
    show_quiz_screen()
else:
    show_result_screen()