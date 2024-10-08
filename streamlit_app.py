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

options = [f"{optionA}", f"{optionB}", f"{optionC}"]

stock = st.radio(label='回答を選択してください',
                 options=options,
                 index=0,
                 horizontal=True)