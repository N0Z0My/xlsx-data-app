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

optionA = s_selected.loc['選択肢A']
optionB = s_selected.loc['選択肢B']
optionC = s_selected.loc['選択肢C']

st.markdown(f'## {question}')

select_button = st.radio(label='回答を選択してください',
                 options= [f"{optionA}", f"{optionB}", f"{optionC}"],
                 index=0,
                 horizontal=True)

if select_button == {optionA}:
   select_button = 0
if select_button == {optionB}:
   select_button = 1
else :
   select_button = 2

st.write(f'選択：{select_button}')

if select_button.value == 0:
  st.write("正解！")
elif select_button.value == 1:
  st.write("不正解！")
elif select_button.value == 2:
   st.write("わからない！")
