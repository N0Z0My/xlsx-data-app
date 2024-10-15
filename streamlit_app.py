import streamlit as st
import pandas as pd
import random
import openai

# OpenAIのAPIキーを設定
openai.api_key = st.secrets["OPENAI_API_KEY"]

def evaluate_answer_with_gpt(question, options, user_answer):
    prompt = f"""
    問題: {question}
    選択肢: {options}
    ユーザーの回答: {user_answer}

    以下の手順で回答を評価してください：
    1. 問題文と選択肢から最も適切な回答を判断してください。
    2. ユーザーの回答が1で判断した最適な回答と一致するか、または同等の意味を持つかを評価してください。
    3. 以下のフォーマットで回答してください：

    最適な回答: [あなたが判断した最適な回答]
    正誤: [正解 or 不正解]
    解説: [簡潔な解説]
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたは豊富に海外旅行にまつわる知識を持っていて、ユーザーの回答を評価する優秀な採点者です。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# 以下、Streamlitアプリケーションのコード（変更なし）
st.set_page_config(page_title='OpenAI-powered Quiz App')
st.title("🎈 OpenAI-powered Radio Quiz")

# データフレームの読み込み
@st.cache_data
def load_data():
    return pd.read_excel('updatelist_kaigai.xlsx', sheet_name='sheet1', index_col=0)

df = load_data()

# セッション状態の初期化
if 'current_question' not in st.session_state:
    st.session_state.current_question = random.randint(0, len(df)-1)
if 'score' not in st.session_state:
    st.session_state.score = 0

with st.expander('データフレーム', expanded=False):
    st.dataframe(df)

# 現在の問題を取得
s_selected = df.loc[st.session_state.current_question]
question = s_selected.loc['問題']
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
            gpt_response = evaluate_answer_with_gpt(question, options, select_button)
        st.write(gpt_response)
        
        if "正解" in gpt_response:
            st.session_state.score += 1
        
        st.write(f"現在のスコア: {st.session_state.score}")
        
        # 次の問題に進むボタン
        if st.button('次の問題へ'):
            st.session_state.current_question = random.randint(0, len(df)-1)
            st.experimental_rerun()

# 現在のスコアを表示
st.sidebar.write(f"現在のスコア: {st.session_state.score}")