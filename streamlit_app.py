import streamlit as st
import pandas as pd
import random
import openai
import os


def check_answer_with_gpt(question, correct_answer, user_answer):
    prompt = f"""
    問題: {question}
    ユーザーの回答: {user_answer}

    ユーザーの回答が正解と同じ意味を持つかどうかを判断し、正誤のみを回答してください：
    正誤: [正解 or 不正解]
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたは海外旅行について豊富な知識を持った、優秀な採点者です。"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message['content']

st.set_page_config(page_title='OpenAI-powered Quiz App')
st.title("💡Quiz")

# データフレームの読み込み
df = pd.read_excel('updatelist_kaigai.xlsx', sheet_name='sheet1', index_col=0)

# セッション状態の初期化
if 'current_question' not in st.session_state:
    st.session_state.current_question = random.randint(0, len(df)-1)
if 'score' not in st.session_state:
    st.session_state.score = 0

with st.expander('df', expanded=False):
    st.table(df)

# 現在の問題を取得
s_selected = df.loc[st.session_state.current_question]
question = s_selected.loc['問題']
optionA = s_selected.loc['選択肢A']
optionB = s_selected.loc['選択肢B']
optionC = s_selected.loc['選択肢C']


st.markdown(f'## {question}')

select_button = st.radio(label='回答を選択してください',
                 options= [f"{optionA}", f"{optionB}", f"{optionC}"],
                 index=0,
                 horizontal=True)

# 回答を確定するボタン
if st.button('回答を確定する'):
    gpt_response = check_answer_with_gpt(question, correct_answer, select_button)
    st.write(gpt_response)
    
    # 次の問題に進むボタン
    if st.button('次の問題へ'):
        st.session_state.current_question = random.randint(0, len(df)-1)
        st.experimental_rerun()
