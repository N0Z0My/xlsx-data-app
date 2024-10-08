import streamlit as st
import pandas as pd
import openpyxl
import random


st.set_page_config(page_title='my new app')
st.title("🎈 My new app")

df = pd.read_excel('list_kaigai.xlsx', sheet_name='sheet1',index_col=0)

with st.expander('df', expanded=False):
    st.table(df)

st.markdown('##### 質問')

len_df = len(df)
 #乱数取得 
num = random.randint(0,len_df-1)
 #dfから行を抽出  series
s_selected = df.loc[num]
 #seriesから値の抽出 
val = s_selected.loc['問題']

st.markdown(f'## {val}') 