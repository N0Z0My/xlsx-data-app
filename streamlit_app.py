import streamlit as st
import pandas as pd
import openpyxl
import random

st.set_page_config(page_title='my new app')
st.title("🎈 Radio Quiz")


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
    if select_button == optionA:
        st.write("えらい！")
        st.session_state.score += 1
    else:
        st.write(f"すごい！")
    
    st.write(f"現在のスコア: {st.session_state.score}")
    
    # 次の問題に進むボタン
    if st.button('次の問題へ'):
        st.session_state.current_question = random.randint(0, len(df)-1)
        st.experimental_rerun()

# 現在のスコアを表示
st.sidebar.write(f"現在のスコア: {st.session_state.score}")