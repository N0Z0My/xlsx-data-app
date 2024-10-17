import streamlit as st
import pandas as pd
import random
from openai import OpenAI
import asyncio

# OpenAIの設定
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

async def evaluate_answer_with_gpt(question, options, user_answer):
    prompt = f"""
    問題: {question}
    選択肢: {options}
    ユーザーの回答: {user_answer}

    以下の手順でユーザーの回答を評価してください：
    1. 問題文と選択肢から最も適切な選択肢を１つ選んでください。
    2. ユーザーの回答が最も適切な選択肢と一致するか評価してください。
    3. 以下のフォーマットで回答してください：

    あなたの回答: {user_answer} [正解 or 不正解]

    正解: [適切な選択肢]

    解説: [正解の短い解説]
    """

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4",
            temperature=0.4,
            messages=[
                {"role": "system", "content": "あなたは海外旅行の豊富な知識を持っていて、ユーザーの回答を評価する優秀な採点者です。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# Streamlitアプリケーションのコード
st.set_page_config(page_title='🤖OpenAI-powered Quiz App')
st.title("💡Quiz")

# データフレームの読み込み
@st.cache_data
def load_data():
    return pd.read_excel('kaigai_latest.xlsx', sheet_name='sheet1', index_col=0)

df = load_data()

# セッション状態の初期化
if 'shuffled_questions' not in st.session_state:
    st.session_state.shuffled_questions = list(range(len(df)))
    random.shuffle(st.session_state.shuffled_questions)
    st.session_state.question_index = 0

# 現在の問題を取得
current_question = st.session_state.shuffled_questions[st.session_state.question_index]
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

# 次の問題に進むボタン
if st.button('次の問題へ'):
    st.session_state.question_index += 1
    if st.session_state.question_index >= len(df):
        st.session_state.question_index = 0
        random.shuffle(st.session_state.shuffled_questions)
    st.rerun()