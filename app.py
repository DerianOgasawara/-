import streamlit as st
import gspread
from datetime import datetime

# 実験プログラムを直接インポート（仲介ファイルなし）
import my_experiment

def get_spreadsheet():
    credentials = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(dict(credentials))
    sh = gc.open_by_url(st.secrets["spreadsheet_url"])
    return sh.sheet1

st.title("本番Web実験ポータル")

participant_id = st.text_input("被験者IDを入力してください:")

if participant_id:
    st.divider()
    
    # インポートした実験プログラムを実行してデータを受け取る
    exp_data = my_experiment.run()
    
    st.divider()

    if st.button("回答を送信する", type="primary"):
        try:
            sheet = get_spreadsheet()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = [timestamp, participant_id] + list(exp_data.values())
            
            sheet.append_row(row_data)
            st.success("正常に保存されました！")
        except Exception as e:
            st.error("送信エラーが発生しました。")
            st.exception(e)
