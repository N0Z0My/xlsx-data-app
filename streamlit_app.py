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
num = random.randint(0, len_df-1)
s_selected = df.loc[num]
question = s_selected.loc['問題']

optionA = s_selected.loc['選択肢A']
optionB = s_selected.loc['選択肢B']
optionC = s_selected.loc['選択肢C']

st.markdown(f'## {question}')

select_button = st.radio(label='回答を選択してください',
                 options= [f"{optionA}", f"{optionB}", f"{optionC}"],
                 index=0,
                 horizontal=True)

st.write(f'選択：{select_button}')

# 選択された回答と正解を比較
if select_button == optionA:
    st.write("正解！")
elif select_button == optionB:
    st.write("不正解！")
elif select_button == optionC:
    st.write("わからない！")