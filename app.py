import streamlit as st
import gspread
from datetime import datetime

# 実験プログラムを直接インポート
import experiment

def get_spreadsheet():
    credentials = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(dict(credentials))
    sh = gc.open_by_url(st.secrets["spreadsheet_url"])
    return sh.sheet1

# 送信済みフラグの初期化
if "submitted" not in st.session_state:
    st.session_state.submitted = False

st.title("Web実験")

participant_id = st.text_input("被験者IDを入力してください:")

if participant_id:
    st.divider()
    
    # インポートした実験プログラムを実行してデータを受け取る
    exp_data = experiment.run()
    
    st.divider()

    # 1. 既に送信が完了している場合
    if st.session_state.submitted:
        st.success("回答は正常に保存されました。ご協力ありがとうございました！\n タブを閉じて終了してください。")

    # 2. 実験が完了しており、まだ送信していない場合（送信ボタンを表示）
    elif exp_data.get("status") == "completed":
        if st.button("回答を送信する", type="primary"):
            try:
                sheet = get_spreadsheet()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row_data = [timestamp, participant_id] + list(exp_data.values())
                
                sheet.append_row(row_data)
                
                # 送信完了フラグを立てて画面を再描画（ボタンを消す）
                st.session_state.submitted = True
                st.rerun()
            except Exception as e:
                st.error("送信エラーが発生しました。")
                st.exception(e)

    # 3. 実験がまだ完了していない場合（送信ボタンを表示しない案内）
    else:
        st.info("実験が完了すると、ここに「回答を送信する」ボタンが表示されます。")
