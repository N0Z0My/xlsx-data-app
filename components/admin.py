import streamlit as st
import pandas as pd
import os
import re
from utils.logger import logger

def show_admin_screen():
    st.title("管理者画面 📊")
    
    # タブの作成
    tab1, tab2 = st.tabs(["📝 ログ閲覧", "📊 統計情報"])

    with tab1:
        show_log_viewer()
    
    with tab2:
        show_statistics()

    if st.button("クイズ画面に戻る"):
        st.session_state.screen = 'quiz'
        st.rerun()

def show_log_viewer():
    st.header("ログ閲覧")
    
    log_files = get_log_files()
    if not log_files:
        st.info("ログファイルが見つかりません")
        return
        
    selected_log = st.selectbox(
        "ログファイルを選択", 
        log_files,
        format_func=lambda x: x.replace('quiz_app_', '').replace('.log', '')
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        show_log_content(selected_log)
    
    with col2:
        provide_log_download(selected_log)

def show_statistics():
    st.header("統計情報")
    
    log_files = get_log_files()
    if not log_files:
        st.info("ログファイルが見つかりません")
        return
        
    selected_log = st.selectbox(
        "統計を表示するログファイルを選択", 
        log_files,
        format_func=lambda x: x.replace('quiz_app_', '').replace('.log', '')
    )
    
    try:
        log_data = parse_log_file(selected_log)
        if log_data:
            display_statistics(log_data)
        else:
            st.info("まだ回答データがありません")
    except Exception as e:
        st.error(f"統計情報の集計に失敗しました: {str(e)}")

def get_log_files():
    return sorted([f for f in os.listdir('logs') if f.startswith('quiz_app_')], reverse=True)

def show_log_content(log_file):
    if st.button("ログを表示"):
        try:
            with open(f"logs/{log_file}", 'r', encoding='utf-8') as f:
                log_contents = f.read()
            st.text_area("ログ内容", log_contents, height=500)
        except Exception as e:
            st.error(f"ログの読み込みに失敗しました: {str(e)}")

def provide_log_download(log_file):
    if st.button("ログをダウンロード"):
        try:
            with open(f"logs/{log_file}", 'r', encoding='utf-8') as f:
                log_contents = f.read()
            st.download_button(
                label="📥 ログファイルをダウンロード",
                data=log_contents,
                file_name=log_file,
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"ログファイルの準備に失敗しました: {str(e)}")

def parse_log_file(log_file):
    with open(f"logs/{log_file}", 'r', encoding='utf-8') as f:
        log_contents = f.readlines()
    
    log_data = []
    current_question = None
    current_timestamp = None
    
    for line in log_contents:
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', line)
        if timestamp_match:
            current_timestamp = timestamp_match.group(1)
        
        question_match = re.search(r'問題表示 - 問題番号: (\d+), 問題: (.+)$', line)
        if question_match:
            current_question = {
                'timestamp': current_timestamp,
                'question_number': question_match.group(1),
                'question': question_match.group(2)
            }
        
        answer_match = re.search(r'(正解|不正解) - 問題番号: (\d+), ユーザー回答: (.+)$', line)
        if answer_match and current_question:
            log_data.append({
                'timestamp': current_timestamp,
                'question_number': answer_match.group(2),
                'question': current_question['question'],
                'user_answer': answer_match.group(3),
                'result': answer_match.group(1)
            })
    
    return log_data

def display_statistics(log_data):
    df_log = pd.DataFrame(log_data)
    
    # 基本統計
    display_basic_stats(df_log)
    
    # エラー数の表示
    display_error_count(df_log)
    
    # データプレビュー
    st.subheader("データプレビュー")
    st.dataframe(df_log.head())
    
    # CSVダウンロード
    provide_csv_download(df_log)
    
    # 詳細分析
    display_detailed_analysis(df_log)

def display_basic_stats(df_log):
    correct_answers = len(df_log[df_log['result'] == '正解'])
    total_attempts = len(df_log)
    accuracy = (correct_answers / total_attempts) * 100 if total_attempts > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="総回答数", value=total_attempts)
    with col2:
        st.metric(label="正解数", value=correct_answers)
    with col3:
        st.metric(label="正答率", value=f"{accuracy:.1f}%")

def display_error_count(df_log):
    try:
        with open(f"logs/{selected_log}", 'r', encoding='utf-8') as f:
            errors = len([line for line in f if "ERROR" in line])
        if errors > 0:
            st.warning(f"エラー発生回数: {errors}回")
    except Exception:
        pass

def provide_csv_download(df_log):
    csv = df_log.to_csv(index=False)
    st.download_button(
        label="📥 CSVファイルをダウンロード",
        data=csv,
        file_name=f"quiz_statistics.csv",
        mime="text/csv"
    )

def display_detailed_analysis(df_log):
    st.subheader("詳細分析")
    
    # 時間帯別の統計
    df_log['hour'] = pd.to_datetime(df_log['timestamp']).dt.hour
    hourly_stats = calculate_hourly_stats(df_log)
    st.write("時間帯別の統計")
    st.dataframe(hourly_stats)
    
    # 問題別の統計
    question_stats = calculate_question_stats(df_log)
    st.write("問題別の統計")
    st.dataframe(question_stats)

def calculate_hourly_stats(df_log):
    return df_log.groupby('hour')['result'].agg({
        '回答数': 'count',
        '正解数': lambda x: (x == '正解').sum()
    }).reset_index()

def calculate_question_stats(df_log):
    return df_log.groupby('question_number')['result'].agg({
        '回答数': 'count',
        '正解数': lambda x: (x == '正解').sum()
    }).reset_index()