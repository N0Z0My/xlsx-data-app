import streamlit as st
import pandas as pd
import openpyxl
import random

st.set_page_config(page_title='my new app')
st.title("🎈 Radio Quiz")

df = pd.read_excel('updatelist_kaigai.xlsx', sheet_name='sheet1', index_col=0)

with st.expander('df', expanded=False):
    st.table(df)

len_df = len(df)
# 乱数取得 
num = random.randint(0, len_df-1)
# dfから行を抽出  series
s_selected = df.loc[num]
# seriesから値の抽出 
question = s_selected.loc['問題']

st.markdown(f'## {question}')

# D, E, F列の値を取得
options = [s_selected.loc['D'], s_selected.loc['E'], s_selected.loc['F']]

# ラジオボタンを表示
selected_option = st.radio("選択肢", options, key="quiz_options")

# 回答を確認するボタン
if st.button("回答を確認"):
    correct_answer = s_selected.loc['正解']
    if selected_option == correct_answer:
        st.success("正解です！")
    else:
        st.error(f"不正解です。正解は {correct_answer} でした。")

# 次の問題ボタン
if st.button("次の問題"):
    st.experimental_rerun()